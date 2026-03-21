"""SpeakLine HTTP Daemon for VS Code Extension.

Exposes JSON API endpoints for voice recording and comment insertion.
Runs as a persistent background process on port 7777.

Usage:
    python -m speakline.daemon
    python -m speakline.daemon --port 8000
"""

import json
import logging
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import unquote

from speakline.commenter import VoiceCommenter, VoiceCommenterError
from speakline.parser import get_language_from_extension

logger = logging.getLogger(__name__)

# Shared state
_commenter: Optional[VoiceCommenter] = None
_recording_lock = threading.Lock()


def _get_commenter() -> VoiceCommenter:
    """Get or create a VoiceCommenter instance."""
    global _commenter
    if _commenter is None:
        _commenter = VoiceCommenter()
    return _commenter


def _uri_to_path(uri: str) -> Optional[str]:
    """Convert file URI to filesystem path."""
    if uri.startswith("file:///"):
        # Windows: file:///C:/path -> C:/path
        path = uri[8:] if len(uri) > 9 and uri[9] == ":" else uri[7:]
    elif uri.startswith("file://"):
        path = uri[7:]
    else:
        path = uri

    # URL decode
    path = unquote(path)

    # Normalize separators
    path = path.replace("/", os.sep)
    return path


class SpeakLineDaemonHandler(BaseHTTPRequestHandler):
    """HTTP request handler for SpeakLine daemon."""

    def do_POST(self) -> None:
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            body = {}
        else:
            try:
                body = json.loads(self.rfile.read(content_length).decode())
            except json.JSONDecodeError:
                self._respond_error("Invalid JSON", 400)
                return

        # Route to handler
        if self.path == "/record":
            result = self._handle_record(body, preview=False)
        elif self.path == "/preview":
            result = self._handle_record(body, preview=True)
        elif self.path == "/transcribe":
            result = self._handle_transcribe(body)
        elif self.path == "/insert":
            result = self._handle_insert(body)
        elif self.path == "/health":
            result = {"ok": True, "status": "ready"}
        else:
            self._respond_error(f"Unknown endpoint: {self.path}", 404)
            return

        self._respond(result)

    def _handle_record(self, body: dict, preview: bool) -> dict:
        """Handle /record or /preview endpoint."""
        try:
            if not all(k in body for k in ["file_uri", "line"]):
                return {"ok": False, "error": "Missing file_uri or line"}

            file_uri = body["file_uri"]
            line_number = int(body["line"]) + 1  # Convert 0-indexed to 1-indexed
            duration = body.get("duration")

            # Convert URI to path
            filepath = _uri_to_path(file_uri)
            if not filepath or not os.path.exists(filepath):
                return {"ok": False, "error": f"File not found: {file_uri}"}

            # Check recording lock
            if not _recording_lock.acquire(blocking=False):
                return {"ok": False, "error": "Recording already in progress"}

            try:
                # Detect language from file
                commenter = _get_commenter()
                ext = os.path.splitext(filepath)[1]
                lang = get_language_from_extension(ext)
                if lang:
                    commenter.language = lang

                # Record and transcribe
                comment = commenter.transcribe_only(duration=duration)

                if not comment.strip():
                    return {"ok": False, "error": "Empty transcription"}

                if preview:
                    return {
                        "ok": True,
                        "comment": comment,
                        "line": line_number,
                        "preview": True,
                    }
                else:
                    # Insert comment into file
                    commenter.insert_comment_to_file(filepath, comment, line_number)
                    return {
                        "ok": True,
                        "comment": comment,
                        "line": line_number,
                        "preview": False,
                    }

            finally:
                _recording_lock.release()

        except VoiceCommenterError as e:
            return {"ok": False, "error": f"SpeakLine error: {e}"}
        except Exception as e:
            logger.exception("Unexpected error during recording")
            return {"ok": False, "error": f"Unexpected error: {e}"}

    def _handle_transcribe(self, body: dict) -> dict:
        """Handle /transcribe endpoint."""
        try:
            duration = body.get("duration")

            if not _recording_lock.acquire(blocking=False):
                return {"ok": False, "error": "Recording already in progress"}

            try:
                commenter = _get_commenter()
                text = commenter.transcribe_only(duration=duration)
                return {"ok": True, "text": text}
            finally:
                _recording_lock.release()

        except VoiceCommenterError as e:
            return {"ok": False, "error": f"SpeakLine error: {e}"}
        except Exception as e:
            logger.exception("Unexpected error during transcription")
            return {"ok": False, "error": f"Unexpected error: {e}"}

    def _handle_insert(self, body: dict) -> dict:
        """Handle /insert endpoint."""
        try:
            if not all(k in body for k in ["file_uri", "line", "comment"]):
                return {"ok": False, "error": "Missing file_uri, line, or comment"}

            file_uri = body["file_uri"]
            line_number = int(body["line"]) + 1  # Convert 0-indexed to 1-indexed
            comment_text = str(body["comment"])

            filepath = _uri_to_path(file_uri)
            if not filepath or not os.path.exists(filepath):
                return {"ok": False, "error": f"File not found: {file_uri}"}

            commenter = _get_commenter()
            ext = os.path.splitext(filepath)[1]
            lang = get_language_from_extension(ext)
            if lang:
                commenter.language = lang

            commenter.insert_comment_to_file(filepath, comment_text, line_number)
            return {"ok": True, "comment": comment_text, "line": line_number}

        except VoiceCommenterError as e:
            return {"ok": False, "error": f"SpeakLine error: {e}"}
        except Exception as e:
            logger.exception("Unexpected error during insert")
            return {"ok": False, "error": f"Unexpected error: {e}"}

    def _respond(self, data: dict, status: int = 200) -> None:
        """Send JSON response."""
        response = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

    def _respond_error(self, error: str, status: int = 400) -> None:
        """Send error JSON response."""
        self._respond({"ok": False, "error": error}, status)

    def log_message(self, format: str, *args) -> None:
        """Suppress default logging."""
        pass


def main() -> None:
    """Start the SpeakLine daemon."""
    import argparse

    parser = argparse.ArgumentParser(description="SpeakLine HTTP Daemon")
    parser.add_argument("--port", type=int, default=7777, help="HTTP port")
    parser.add_argument(
        "--log", type=str, default=None, help="Log file path"
    )
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(
            filename=args.log, level=logging.DEBUG, format="%(asctime)s %(message)s"
        )
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info(f"Starting SpeakLine daemon on port {args.port}")
    server = HTTPServer(("127.0.0.1", args.port), SpeakLineDaemonHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Daemon shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
