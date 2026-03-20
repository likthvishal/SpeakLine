"""SpeakLine - Record voice and insert as inline code comments.

This package provides tools for recording voice input, transcribing it to text,
and inserting the transcribed text as comments in source code files.

Example:
    >>> from speakline import VoiceCommenter
    >>> commenter = VoiceCommenter()
    >>> commenter.record_and_insert('myfile.py', line_number=42)

    >>> # Transcribe only (no file modification)
    >>> text = commenter.transcribe_only()

    >>> # Insert comment into code string
    >>> code = "def foo():\\n    pass"
    >>> updated = commenter.insert_comment_to_string(code, "My comment", 2)
"""

__version__ = "0.3.1"

from .commenter import VoiceCommenter, VoiceCommenterError
from .recorder import (
    AudioConfig,
    SilenceConfig,
    RecorderBase,
    LocalAudioRecorder,
    MockRecorder,
    RecorderError,
    AudioDeviceError,
)
from .transcriber import (
    TranscriberBase,
    WhisperTranscriber,
    OpenAITranscriber,
    MockTranscriber,
    TranscriberError,
    ModelNotFoundError,
    APIError,
    get_transcriber,
)
from .formatter import (
    FormatterBase,
    RuleBasedFormatter,
    LLMFormatter,
    PassthroughFormatter,
    FormatterError,
    get_formatter,
)
from .parser import (
    ParserBase,
    GenericParser,
    PythonParser,
    JavaScriptParser,
    TypeScriptParser,
    GoParser,
    RustParser,
    JavaParser,
    CSharpParser,
    RubyParser,
    CppParser,
    get_parser,
    get_language_from_extension,
    ParserError,
    InvalidLineNumberError,
)

__all__ = [
    # Version
    "__version__",
    # Main class
    "VoiceCommenter",
    "VoiceCommenterError",
    # Recorder
    "AudioConfig",
    "SilenceConfig",
    "RecorderBase",
    "LocalAudioRecorder",
    "MockRecorder",
    "RecorderError",
    "AudioDeviceError",
    # Transcriber
    "TranscriberBase",
    "WhisperTranscriber",
    "OpenAITranscriber",
    "MockTranscriber",
    "TranscriberError",
    "ModelNotFoundError",
    "APIError",
    "get_transcriber",
    # Formatter
    "FormatterBase",
    "RuleBasedFormatter",
    "LLMFormatter",
    "PassthroughFormatter",
    "FormatterError",
    "get_formatter",
    # Parser
    "ParserBase",
    "GenericParser",
    "PythonParser",
    "JavaScriptParser",
    "TypeScriptParser",
    "GoParser",
    "RustParser",
    "JavaParser",
    "CSharpParser",
    "RubyParser",
    "CppParser",
    "get_parser",
    "get_language_from_extension",
    "ParserError",
    "InvalidLineNumberError",
]
