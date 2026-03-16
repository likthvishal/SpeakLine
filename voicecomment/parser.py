"""Code parsing module for language-aware comment insertion."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Type
import logging
import re

logger = logging.getLogger(__name__)


class ParserError(Exception):
    """Base exception for parser errors."""

    pass


class InvalidLineNumberError(ParserError):
    """Error when line number is invalid."""

    pass


class ParserBase(ABC):
    """Abstract base class for code parsers."""

    # Comment prefix for the language
    comment_prefix: str = "#"

    @abstractmethod
    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert a comment at the specified line number.

        Args:
            code: Source code string.
            comment: Comment text to insert.
            line_number: Line number to insert the comment at (1-indexed).

        Returns:
            Modified code with the comment inserted.

        Raises:
            ParserError: If insertion fails.
            InvalidLineNumberError: If line number is out of range.
        """
        pass

    def _get_indentation(self, line: str) -> str:
        """Extract leading whitespace from a line."""
        match = re.match(r"^(\s*)", line)
        return match.group(1) if match else ""

    def _format_comment(self, comment: str, indentation: str = "") -> str:
        """Format comment text with proper prefix and indentation."""
        # Handle multi-line comments
        lines = comment.strip().split("\n")
        formatted_lines = []

        for line in lines:
            formatted_lines.append(f"{indentation}{self.comment_prefix} {line.strip()}")

        return "\n".join(formatted_lines)


class GenericParser(ParserBase):
    """Generic parser that works with any language using configurable comment prefix."""

    def __init__(self, comment_prefix: str = "#") -> None:
        """Initialize generic parser.

        Args:
            comment_prefix: Comment prefix for the language.
        """
        self.comment_prefix = comment_prefix

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert comment at the specified line.

        The comment is inserted before the target line, preserving the
        indentation of the target line.

        Args:
            code: Source code string.
            comment: Comment text to insert.
            line_number: Line number (1-indexed) to insert the comment before.

        Returns:
            Code with the comment inserted.

        Raises:
            InvalidLineNumberError: If line number is out of range.
        """
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        # Get indentation from target line (or previous line if inserting at end)
        if line_number <= len(lines):
            target_line = lines[line_number - 1]
        else:
            target_line = lines[-1] if lines else ""

        indentation = self._get_indentation(target_line)
        formatted_comment = self._format_comment(comment, indentation)

        # Insert comment before the target line
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class PythonParser(ParserBase):
    """Parser for Python code with # comments."""

    comment_prefix = "#"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert Python comment at the specified line.

        Args:
            code: Python source code.
            comment: Comment text to insert.
            line_number: Line number (1-indexed) to insert the comment before.

        Returns:
            Code with the comment inserted.

        Raises:
            InvalidLineNumberError: If line number is out of range.
        """
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        # Get indentation from target line
        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            # Inserting at end, use previous line's indentation
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class JavaScriptParser(ParserBase):
    """Parser for JavaScript/TypeScript code with // comments."""

    comment_prefix = "//"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert JavaScript comment at the specified line.

        Args:
            code: JavaScript/TypeScript source code.
            comment: Comment text to insert.
            line_number: Line number (1-indexed) to insert the comment before.

        Returns:
            Code with the comment inserted.

        Raises:
            InvalidLineNumberError: If line number is out of range.
        """
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class TypeScriptParser(JavaScriptParser):
    """Parser for TypeScript code (inherits from JavaScript)."""

    pass


class GoParser(ParserBase):
    """Parser for Go code with // comments."""

    comment_prefix = "//"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert Go comment at the specified line.

        Args:
            code: Go source code.
            comment: Comment text to insert.
            line_number: Line number (1-indexed) to insert the comment before.

        Returns:
            Code with the comment inserted.

        Raises:
            InvalidLineNumberError: If line number is out of range.
        """
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class RustParser(ParserBase):
    """Parser for Rust code with // comments."""

    comment_prefix = "//"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert Rust comment at the specified line."""
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class JavaParser(ParserBase):
    """Parser for Java code with // comments."""

    comment_prefix = "//"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert Java comment at the specified line."""
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class CSharpParser(ParserBase):
    """Parser for C# code with // comments."""

    comment_prefix = "//"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert C# comment at the specified line."""
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class RubyParser(ParserBase):
    """Parser for Ruby code with # comments."""

    comment_prefix = "#"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert Ruby comment at the specified line."""
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


class CppParser(ParserBase):
    """Parser for C/C++ code with // comments."""

    comment_prefix = "//"

    def insert_comment(self, code: str, comment: str, line_number: int) -> str:
        """Insert C/C++ comment at the specified line."""
        lines = code.split("\n")

        if line_number < 1 or line_number > len(lines) + 1:
            raise InvalidLineNumberError(
                f"Line number {line_number} is out of range (1-{len(lines) + 1})"
            )

        if line_number <= len(lines):
            target_line = lines[line_number - 1]
            indentation = self._get_indentation(target_line)
        else:
            indentation = self._get_indentation(lines[-1]) if lines else ""

        formatted_comment = self._format_comment(comment, indentation)
        lines.insert(line_number - 1, formatted_comment)

        return "\n".join(lines)


# Language extension to parser mapping
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

# File extension to language mapping
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


def get_language_from_extension(filepath: str) -> Optional[str]:
    """Determine the programming language from file extension.

    Args:
        filepath: Path to the source file.

    Returns:
        Language name or None if not recognized.
    """
    import os

    _, ext = os.path.splitext(filepath.lower())
    return EXTENSION_TO_LANGUAGE.get(ext)


def get_parser(language: Optional[str] = None, filepath: Optional[str] = None) -> ParserBase:
    """Get a parser for the specified language or file.

    Args:
        language: Language name (e.g., 'python', 'javascript').
        filepath: Path to source file (used to detect language if language is None).

    Returns:
        Parser instance for the language.

    Raises:
        ParserError: If no parser is available for the language.
    """
    # Try to detect language from file extension
    if language is None and filepath:
        language = get_language_from_extension(filepath)

    if language is None:
        logger.warning("Could not detect language, using generic parser")
        return GenericParser()

    language = language.lower()

    if language in LANGUAGE_PARSERS:
        return LANGUAGE_PARSERS[language]()

    # Check for common aliases
    aliases = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "cs": "csharp",
        "c#": "csharp",
        "c++": "cpp",
    }

    if language in aliases:
        return LANGUAGE_PARSERS[aliases[language]]()

    logger.warning(f"Unknown language '{language}', using generic parser")
    return GenericParser()
