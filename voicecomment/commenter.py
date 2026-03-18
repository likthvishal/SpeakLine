"""Main orchestration module for VoiceComment."""

from typing import Optional
import logging
import os

from .recorder import (
    RecorderBase,
    LocalAudioRecorder,
    AudioConfig,
    RecorderError,
)
from .transcriber import (
    TranscriberBase,
    WhisperTranscriber,
    TranscriberError,
)
from .parser import (
    ParserBase,
    get_parser,
    get_language_from_extension,
    ParserError,
)

logger = logging.getLogger(__name__)


class VoiceCommenterError(Exception):
    """Base exception for VoiceCommenter errors."""

    pass


class VoiceCommenter:
    """Main class for recording voice and inserting comments into code.

    This class orchestrates the recording, transcription, and comment insertion
    process. It supports multiple languages and pluggable backends.

    Example:
        >>> commenter = VoiceCommenter()
        >>> commenter.record_and_insert('myfile.py', line_number=42)

        >>> # Transcribe only
        >>> text = commenter.transcribe_only()

        >>> # Insert comment to string (no file I/O)
        >>> code = "def foo():\\n    pass"
        >>> updated = commenter.insert_comment_to_string(code, "My comment", 2)
    """

    def __init__(
        self,
        language: Optional[str] = None,
        transcriber: Optional[TranscriberBase] = None,
        recorder: Optional[RecorderBase] = None,
        audio_config: Optional[AudioConfig] = None,
    ) -> None:
        """Initialize the VoiceCommenter.

        Args:
            language: Programming language for comment formatting.
                If None, auto-detects from file extension.
            transcriber: Transcription backend. Defaults to WhisperTranscriber.
            recorder: Audio recorder. Defaults to LocalAudioRecorder.
            audio_config: Audio configuration for the recorder.
        """
        self._language = language
        self._audio_config = audio_config or AudioConfig()
        self._recorder = recorder or LocalAudioRecorder(config=self._audio_config)
        self._transcriber = transcriber or self._create_default_transcriber()

    def _create_default_transcriber(self) -> TranscriberBase:
        """Create the default transcriber with fallback logic."""
        try:
            return WhisperTranscriber(model_size="base")
        except Exception as e:
            logger.warning(f"Failed to create Whisper transcriber: {e}")
            # Could add OpenAI fallback here
            raise VoiceCommenterError(
                "Could not initialize transcriber. "
                "Ensure openai-whisper is installed: pip install openai-whisper"
            )

    def _get_parser(self, filepath: Optional[str] = None) -> ParserBase:
        """Get parser for the configured or detected language."""
        return get_parser(language=self._language, filepath=filepath)

    def record_and_insert(
        self,
        filepath: str,
        line_number: int,
        duration: Optional[float] = None,
    ) -> str:
        """Record voice, transcribe, and insert comment into file.

        This is the main workflow method. It records audio from the microphone,
        transcribes it to text, and inserts the resulting comment into the
        specified file at the given line number.

        Args:
            filepath: Path to the source file to modify.
            line_number: Line number (1-indexed) to insert the comment before.
            duration: Fixed recording duration in seconds. If None, uses
                silence detection to stop recording.

        Returns:
            The transcribed comment text.

        Raises:
            VoiceCommenterError: If any step fails.
            FileNotFoundError: If the file doesn't exist.
        """
        # Validate filepath to prevent path traversal
        self._validate_filepath(filepath)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Record audio
        logger.info(f"Recording audio for {filepath}:{line_number}")
        try:
            audio = self._recorder.record(duration=duration)
        except RecorderError as e:
            raise VoiceCommenterError(f"Recording failed: {e}")

        # Transcribe
        logger.info("Transcribing audio...")
        try:
            comment = self._transcriber.transcribe(
                audio,
                sample_rate=self._recorder.sample_rate,
            )
        except TranscriberError as e:
            raise VoiceCommenterError(f"Transcription failed: {e}")

        if not comment.strip():
            logger.warning("Transcription resulted in empty text")
            raise VoiceCommenterError("Transcription resulted in empty text")

        # Insert comment into file
        self.insert_comment_to_file(filepath, comment, line_number)

        logger.info(f"Comment inserted at line {line_number}")
        return comment

    def transcribe_only(
        self,
        duration: Optional[float] = None,
    ) -> str:
        """Record and transcribe without modifying any files.

        Args:
            duration: Fixed recording duration in seconds. If None, uses
                silence detection.

        Returns:
            Transcribed text.

        Raises:
            VoiceCommenterError: If recording or transcription fails.
        """
        logger.info("Recording audio for transcription...")
        try:
            audio = self._recorder.record(duration=duration)
        except RecorderError as e:
            raise VoiceCommenterError(f"Recording failed: {e}")

        logger.info("Transcribing audio...")
        try:
            text = self._transcriber.transcribe(
                audio,
                sample_rate=self._recorder.sample_rate,
            )
        except TranscriberError as e:
            raise VoiceCommenterError(f"Transcription failed: {e}")

        return text

    def insert_comment_to_string(
        self,
        code: str,
        comment: str,
        line_number: int,
        language: Optional[str] = None,
    ) -> str:
        """Insert a comment into a code string without file I/O.

        This method is useful for programmatic comment insertion, such as
        in Jupyter notebooks or editor extensions.

        Args:
            code: Source code string.
            comment: Comment text to insert.
            line_number: Line number (1-indexed) to insert the comment before.
            language: Override language detection. If None, uses the
                commenter's configured language.

        Returns:
            Modified code with the comment inserted.

        Raises:
            VoiceCommenterError: If comment insertion fails.
        """
        lang = language or self._language
        parser = get_parser(language=lang)

        try:
            return parser.insert_comment(code, comment, line_number)
        except ParserError as e:
            raise VoiceCommenterError(f"Failed to insert comment: {e}")

    def insert_comment_to_file(
        self,
        filepath: str,
        comment: str,
        line_number: int,
    ) -> None:
        """Insert a comment into a file at the specified line.

        Args:
            filepath: Path to the source file.
            comment: Comment text to insert.
            line_number: Line number (1-indexed) to insert the comment before.

        Raises:
            VoiceCommenterError: If insertion fails.
            FileNotFoundError: If the file doesn't exist.
        """
        # Validate filepath to prevent path traversal
        self._validate_filepath(filepath)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read file with encoding detection
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except UnicodeDecodeError:
            logger.warning(f"File {filepath} is not UTF-8, attempting latin-1")
            try:
                with open(filepath, "r", encoding="latin-1") as f:
                    code = f.read()
            except Exception as e:
                raise VoiceCommenterError(f"Cannot read file (unsupported encoding): {e}")

        # Get parser for file
        parser = self._get_parser(filepath)

        # Insert comment
        try:
            updated_code = parser.insert_comment(code, comment, line_number)
        except ParserError as e:
            raise VoiceCommenterError(f"Failed to insert comment: {e}")

        # Write back atomically (to temp file first, then rename)
        import tempfile

        try:
            # Write to temporary file in same directory for atomic rename
            temp_fd, temp_path = tempfile.mkstemp(
                dir=os.path.dirname(filepath) or ".",
                text=True
            )
            try:
                with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                    f.write(updated_code)
                # Atomic rename
                os.replace(temp_path, filepath)
            except Exception:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise
        except Exception as e:
            raise VoiceCommenterError(f"Failed to write file: {e}")

        logger.info(f"Comment written to {filepath}:{line_number}")

    def _validate_filepath(self, filepath: str) -> None:
        """Validate filepath to prevent directory traversal attacks.

        Args:
            filepath: Path to validate.

        Raises:
            VoiceCommenterError: If path is invalid or tries to escape.
        """
        # Reject null bytes
        if "\x00" in filepath:
            raise VoiceCommenterError("Invalid filepath: contains null bytes")

        # Reject attempts to write to system directories
        abs_path = os.path.abspath(filepath)
        if abs_path.startswith(("/etc", "/sys", "/proc")) or abs_path.startswith(("C:\\Windows", "C:\\Program Files")):
            raise VoiceCommenterError(f"Cannot modify system files: {filepath}")

    @property
    def language(self) -> Optional[str]:
        """Return the configured language."""
        return self._language

    @language.setter
    def language(self, value: Optional[str]) -> None:
        """Set the language for comment formatting."""
        self._language = value

    @property
    def recorder(self) -> RecorderBase:
        """Return the audio recorder."""
        return self._recorder

    @property
    def transcriber(self) -> TranscriberBase:
        """Return the transcriber."""
        return self._transcriber
