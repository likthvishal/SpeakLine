"""SpeakLine LSP Server.

Provides bidirectional communication between IDE extensions and SpeakLine core.
Handles cursor position, active file context, and indent-aware comment insertion.

Usage:
    python -m speakline.lsp.server          # stdio (default)
    python -m speakline.lsp.server --tcp 2087  # tcp mode
"""

import json
import logging
import os
import threading
from typing import Optional

from pygls.lsp.server import LanguageServer
from lsprotocol import types

from speakline.commenter import VoiceCommenter, VoiceCommenterError
from speakline.parser import get_language_from_extension
from speakline.transcriber import WhisperTranscriber, OpenAITranscriber, MockTranscriber
from speakline.formatter import get_formatter

logger = logging.getLogger(__name__)

# Server instance
server = LanguageServer("speakline-lsp", "v0.2.0")

# Shared state
_commenter: Optional[VoiceCommenter] = None
_recording_lock = threading.Lock()


def _get_commenter(backend: str = "whisper", model_size: str = "base") -> VoiceCommenter:
    """Get or create a VoiceCommenter instance."""
    global _commenter
    if _commenter is None:
        _commenter = VoiceCommenter()
    return _commenter


@server.feature(types.INITIALIZE)
def on_initialize(params: types.InitializeParams) -> types.InitializeResult:
    """Handle LSP initialize request."""
    logger.info("SpeakLine LSP server initializing...")
    return types.InitializeResult(
        capabilities=types.ServerCapabilities(
            execute_command_provider=types.ExecuteCommandOptions(
                commands=[
                    "speakline.recordAtCursor",
                    "speakline.recordAtCursorPreview",
                    "speakline.transcribeOnly",
                    "speakline.insertComment",
                ]
            ),
            text_document_sync=types.TextDocumentSyncOptions(
                open_close=True,
                change=types.TextDocumentSyncKind.Full,
            ),
        ),
        server_info=types.ServerInfo(name="speakline-lsp", version="0.2.0"),
    )


@server.feature(types.WORKSPACE_EXECUTE_COMMAND)
def on_execute_command(params: types.ExecuteCommandParams) -> Optional[str]:
    """Handle custom commands from the VS Code extension."""
    command = params.command
    args = params.arguments or []

    if command == "speakline.recordAtCursor":
        return _handle_record_at_cursor(args, preview=False)
    elif command == "speakline.recordAtCursorPreview":
        return _handle_record_at_cursor(args, preview=True)
    elif command == "speakline.transcribeOnly":
        return _handle_transcribe_only(args)
    elif command == "speakline.insertComment":
        return _handle_insert_comment(args)
    else:
        server.show_message(f"Unknown command: {command}", types.MessageType.Error)
        return None


def _handle_record_at_cursor(args: list, preview: bool = False) -> Optional[str]:
    """Record voice at the cursor position and insert comment.

    Args from extension: [file_uri, line_number (0-indexed), duration?]
    """
    if len(args) < 2:
        server.show_message(
            "Missing arguments: file URI and line number required",
            types.MessageType.Error,
        )
        return None

    file_uri = args[0]
    line_number = int(args[1]) + 1  # Convert 0-indexed to 1-indexed
    duration = float(args[2]) if len(args) > 2 else None

    # Convert URI to file path
    filepath = _uri_to_path(file_uri)
    if not filepath or not os.path.exists(filepath):
        server.show_message(f"File not found: {file_uri}", types.MessageType.Error)
        return None

    if not _recording_lock.acquire(blocking=False):
        server.show_message("Recording already in progress", types.MessageType.Warning)
        return None

    try:
        server.show_message("Recording... speak now", types.MessageType.Info)

        commenter = _get_commenter()

        # Detect language from file
        ext = os.path.splitext(filepath)[1]
        lang = get_language_from_extension(ext)
        if lang:
            commenter.language = lang

        # Record and transcribe
        comment = commenter.transcribe_only(duration=duration)

        if not comment.strip():
            server.show_message("Empty transcription", types.MessageType.Warning)
            return None

        if preview:
            # Send preview back to extension without modifying file
            server.show_message(
                f"Preview: {comment}",
                types.MessageType.Info,
            )
            return json.dumps({"comment": comment, "line": line_number, "preview": True})
        else:
            # Insert comment into file
            commenter.insert_comment_to_file(filepath, comment, line_number)
            server.show_message(
                f"Comment inserted at line {line_number}",
                types.MessageType.Info,
            )
            return json.dumps({"comment": comment, "line": line_number, "preview": False})

    except VoiceCommenterError as e:
        server.show_message(f"SpeakLine error: {e}", types.MessageType.Error)
        return None
    except Exception as e:
        server.show_message(f"Unexpected error: {e}", types.MessageType.Error)
        logger.exception("Unexpected error during recording")
        return None
    finally:
        _recording_lock.release()


def _handle_transcribe_only(args: list) -> Optional[str]:
    """Record and transcribe without inserting.

    Args from extension: [duration?]
    """
    duration = float(args[0]) if args else None

    if not _recording_lock.acquire(blocking=False):
        server.show_message("Recording already in progress", types.MessageType.Warning)
        return None

    try:
        server.show_message("Recording... speak now", types.MessageType.Info)
        commenter = _get_commenter()
        text = commenter.transcribe_only(duration=duration)
        server.show_message(f"Transcription: {text}", types.MessageType.Info)
        return json.dumps({"text": text})
    except VoiceCommenterError as e:
        server.show_message(f"SpeakLine error: {e}", types.MessageType.Error)
        return None
    finally:
        _recording_lock.release()


def _handle_insert_comment(args: list) -> Optional[str]:
    """Insert a comment directly without recording.

    Args from extension: [file_uri, line_number (0-indexed), comment_text]
    """
    if len(args) < 3:
        server.show_message(
            "Missing arguments: file URI, line number, and comment required",
            types.MessageType.Error,
        )
        return None

    file_uri = args[0]
    line_number = int(args[1]) + 1  # Convert 0-indexed to 1-indexed
    comment_text = str(args[2])

    filepath = _uri_to_path(file_uri)
    if not filepath or not os.path.exists(filepath):
        server.show_message(f"File not found: {file_uri}", types.MessageType.Error)
        return None

    try:
        commenter = _get_commenter()
        ext = os.path.splitext(filepath)[1]
        lang = get_language_from_extension(ext)
        if lang:
            commenter.language = lang

        commenter.insert_comment_to_file(filepath, comment_text, line_number)
        server.show_message(
            f"Comment inserted at line {line_number}",
            types.MessageType.Info,
        )
        return json.dumps({"comment": comment_text, "line": line_number})
    except VoiceCommenterError as e:
        server.show_message(f"SpeakLine error: {e}", types.MessageType.Error)
        return None


def _uri_to_path(uri: str) -> Optional[str]:
    """Convert a file URI to a filesystem path."""
    if uri.startswith("file:///"):
        # Windows: file:///C:/path -> C:/path
        path = uri[8:] if len(uri) > 9 and uri[9] == ":" else uri[7:]
    elif uri.startswith("file://"):
        path = uri[7:]
    else:
        path = uri

    # URL decode
    from urllib.parse import unquote
    path = unquote(path)

    # Normalize separators
    path = path.replace("/", os.sep)
    return path


def main() -> None:
    """Entry point for the LSP server."""
    import argparse

    parser = argparse.ArgumentParser(description="SpeakLine LSP Server")
    parser.add_argument(
        "--tcp", type=int, default=None, help="Run in TCP mode on specified port"
    )
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

    if args.tcp:
        server.start_tcp("127.0.0.1", args.tcp)
    else:
        server.start_io()


if __name__ == "__main__":
    main()
