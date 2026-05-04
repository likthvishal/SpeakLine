"""Code parsing module for language-aware comment insertion."""

from typing import Optional, Dict, Type
import logging
import os
import re

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Base exception for parser errors."""

    pass


class InvalidLineNumberError(ParserError):
    """Error when line number is invalid."""

    pass


class ParserBase:
    """Base class for line-comment parsers.

    Subclasses set ``comment_prefix`` for their language. The insertion
    algorithm is identical across single-line-comment languages, so it
    lives here.
    """

    comment_prefix: str = "#"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert a comment before ``line_number`` (1-indexed).

        Indentation is taken from the target line (or the previous line
        when inserting at the end of the file).

        Raises:
            InvalidLineNumberError: If ``line_number`` is not an int or out of range.
        """
        if not isinstance(line_number, int) or isinstance(line_number, bool):
            raise InvalidLineNumberError(
                f"Line number must be an integer, got {type(line_number).__name__}"
            )

        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
        else:
            target_line = lines[-1] if lines else ""

        indentation = self._get_indentation(target_line)
        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)

    def _get_indentation(self, line: str) -> str:
        match = re.match(r"^(\s*)", line)
        return match.group(1) if match else ""

    def _format_comment(self, comment: str, indentation: str = "") -> str:
        lines = comment.strip().split("\n")
        return "\n".join(f"{indentation}{self.comment_prefix} {ln.strip()}" for ln in lines)


class GenericParser(ParserBase):
    """Parser with a runtime-configurable comment prefix."""

    def __init__(self, comment_prefix: str = "#") -> None:
        self.comment_prefix = comment_prefix


class PythonParser(ParserBase):
    comment_prefix = "#"


class JavaScriptParser(ParserBase):
    comment_prefix = "//"


class TypeScriptParser(JavaScriptParser):
    pass


class GoParser(ParserBase):
    comment_prefix = "//"


class RustParser(ParserBase):
    comment_prefix = "//"


class JavaParser(ParserBase):
    comment_prefix = "//"


class CSharpParser(ParserBase):
    comment_prefix = "//"


class RubyParser(ParserBase):
    comment_prefix = "#"


class CppParser(ParserBase):
    comment_prefix = "//"


LANGUAGE_PARSERS: Dict[str, Type[ParserBase]] = {
    "python": PythonParser,
    "javascript": JavaScriptParser,
    "typescript": TypeScriptParser,
    "go": GoParser,
    "rust": RustParser,
    "java": JavaParser,
    "csharp": CSharpParser,
    "ruby": RubyParser,
    "c": CppParser,
    "cpp": CppParser,
}

EXTENSION_TO_LANGUAGE: Dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cs": "csharp",
    ".rb": "ruby",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
}

LANGUAGE_ALIASES: Dict[str, str] = {
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "cs": "csharp",
    "c#": "csharp",
    "c++": "cpp",
}


def get_language_from_extension(filepath: str) -> Optional[str]:
    """Determine the programming language from file extension."""
    _, ext = os.path.splitext(filepath.lower())
    return EXTENSION_TO_LANGUAGE.get(ext)


def get_parser(language: Optional[str] = None, filepath: Optional[str] = None) -> ParserBase:
    """Get a parser for the specified language or file.

    Falls back to ``GenericParser`` when the language is unknown.
    """
    if language is None and filepath:
        language = get_language_from_extension(filepath)

    if language is None:
        logger.warning("Could not detect language, using generic parser")
        return GenericParser()

    language = language.lower()
    resolved = LANGUAGE_ALIASES.get(language, language)

    if resolved in LANGUAGE_PARSERS:
        return LANGUAGE_PARSERS[resolved]()

    logger.warning(f"Unknown language '{language}', using generic parser")
    return GenericParser()
