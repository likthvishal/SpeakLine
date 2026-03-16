"""Tests for the parser module."""

import pytest

from voicecomment.parser import (
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
    InvalidLineNumberError,
)


class TestGenericParser:
    """Tests for GenericParser class."""

    def test_inherits_from_base(self):
        """Test that GenericParser inherits from ParserBase."""
        parser = GenericParser()
        assert isinstance(parser, ParserBase)

    def test_default_comment_prefix(self):
        """Test default comment prefix is #."""
        parser = GenericParser()
        assert parser.comment_prefix == "#"

    def test_custom_comment_prefix(self):
        """Test custom comment prefix."""
        parser = GenericParser(comment_prefix="//")
        assert parser.comment_prefix == "//"

    def test_insert_comment_at_line_1(self):
        """Test inserting comment at first line."""
        parser = GenericParser()
        code = "print('hello')"
        result = parser.insert_comment(code, "Say hello", 1)
        lines = result.split("\n")
        assert lines[0] == "# Say hello"
        assert lines[1] == "print('hello')"

    def test_insert_comment_preserves_indentation(self):
        """Test that comment preserves target line indentation."""
        parser = GenericParser()
        code = "def foo():\n    return 42"
        result = parser.insert_comment(code, "Return value", 2)
        lines = result.split("\n")
        assert lines[1] == "    # Return value"
        assert lines[2] == "    return 42"

    def test_insert_comment_middle_of_file(self):
        """Test inserting comment in middle of file."""
        parser = GenericParser()
        code = "line1\nline2\nline3"
        result = parser.insert_comment(code, "Before line 2", 2)
        lines = result.split("\n")
        assert lines[0] == "line1"
        assert lines[1] == "# Before line 2"
        assert lines[2] == "line2"
        assert lines[3] == "line3"

    def test_insert_comment_invalid_line_zero(self):
        """Test that line 0 raises error."""
        parser = GenericParser()
        with pytest.raises(InvalidLineNumberError):
            parser.insert_comment("code", "comment", 0)

    def test_insert_comment_invalid_line_negative(self):
        """Test that negative line raises error."""
        parser = GenericParser()
        with pytest.raises(InvalidLineNumberError):
            parser.insert_comment("code", "comment", -1)

    def test_insert_comment_invalid_line_too_large(self):
        """Test that too large line number raises error."""
        parser = GenericParser()
        code = "line1\nline2"  # 2 lines
        with pytest.raises(InvalidLineNumberError):
            parser.insert_comment(code, "comment", 4)


class TestPythonParser:
    """Tests for PythonParser class."""

    def test_comment_prefix(self):
        """Test Python comment prefix."""
        parser = PythonParser()
        assert parser.comment_prefix == "#"

    def test_insert_comment(self):
        """Test inserting Python comment."""
        parser = PythonParser()
        code = "def factorial(n):\n    return n * factorial(n - 1) if n > 1 else 1"
        result = parser.insert_comment(code, "Calculate factorial recursively", 2)
        lines = result.split("\n")
        assert lines[1] == "    # Calculate factorial recursively"

    def test_insert_at_function_definition(self):
        """Test inserting comment before function definition."""
        parser = PythonParser()
        code = "import os\n\ndef main():\n    pass"
        result = parser.insert_comment(code, "Main entry point", 3)
        lines = result.split("\n")
        assert "# Main entry point" in lines[2]


class TestJavaScriptParser:
    """Tests for JavaScriptParser class."""

    def test_comment_prefix(self):
        """Test JavaScript comment prefix."""
        parser = JavaScriptParser()
        assert parser.comment_prefix == "//"

    def test_insert_comment(self):
        """Test inserting JavaScript comment."""
        parser = JavaScriptParser()
        code = "function greet() {\n    console.log('Hello');\n}"
        result = parser.insert_comment(code, "Log greeting", 2)
        lines = result.split("\n")
        assert lines[1] == "    // Log greeting"


class TestTypeScriptParser:
    """Tests for TypeScriptParser class."""

    def test_inherits_from_javascript(self):
        """Test TypeScriptParser inherits from JavaScriptParser."""
        parser = TypeScriptParser()
        assert isinstance(parser, JavaScriptParser)


class TestGoParser:
    """Tests for GoParser class."""

    def test_comment_prefix(self):
        """Test Go comment prefix."""
        parser = GoParser()
        assert parser.comment_prefix == "//"

    def test_insert_comment(self):
        """Test inserting Go comment."""
        parser = GoParser()
        code = "func main() {\n\tfmt.Println(\"Hello\")\n}"
        result = parser.insert_comment(code, "Print hello", 2)
        lines = result.split("\n")
        assert "// Print hello" in lines[1]


class TestRustParser:
    """Tests for RustParser class."""

    def test_comment_prefix(self):
        """Test Rust comment prefix."""
        parser = RustParser()
        assert parser.comment_prefix == "//"


class TestJavaParser:
    """Tests for JavaParser class."""

    def test_comment_prefix(self):
        """Test Java comment prefix."""
        parser = JavaParser()
        assert parser.comment_prefix == "//"


class TestCSharpParser:
    """Tests for CSharpParser class."""

    def test_comment_prefix(self):
        """Test C# comment prefix."""
        parser = CSharpParser()
        assert parser.comment_prefix == "//"


class TestRubyParser:
    """Tests for RubyParser class."""

    def test_comment_prefix(self):
        """Test Ruby comment prefix."""
        parser = RubyParser()
        assert parser.comment_prefix == "#"


class TestCppParser:
    """Tests for CppParser class."""

    def test_comment_prefix(self):
        """Test C++ comment prefix."""
        parser = CppParser()
        assert parser.comment_prefix == "//"


class TestGetLanguageFromExtension:
    """Tests for get_language_from_extension function."""

    @pytest.mark.parametrize(
        "filepath,expected",
        [
            ("file.py", "python"),
            ("file.pyw", "python"),
            ("file.js", "javascript"),
            ("file.jsx", "javascript"),
            ("file.ts", "typescript"),
            ("file.tsx", "typescript"),
            ("file.go", "go"),
            ("file.rs", "rust"),
            ("file.java", "java"),
            ("file.cs", "csharp"),
            ("file.rb", "ruby"),
            ("file.c", "c"),
            ("file.cpp", "cpp"),
            ("file.h", "c"),
            ("file.hpp", "cpp"),
        ],
    )
    def test_known_extensions(self, filepath, expected):
        """Test known file extensions."""
        assert get_language_from_extension(filepath) == expected

    def test_unknown_extension(self):
        """Test unknown file extension returns None."""
        assert get_language_from_extension("file.xyz") is None

    def test_case_insensitive(self):
        """Test extension matching is case insensitive."""
        assert get_language_from_extension("file.PY") == "python"
        assert get_language_from_extension("file.Js") == "javascript"


class TestGetParser:
    """Tests for get_parser factory function."""

    def test_get_python_parser(self):
        """Test getting Python parser by language."""
        parser = get_parser(language="python")
        assert isinstance(parser, PythonParser)

    def test_get_javascript_parser(self):
        """Test getting JavaScript parser by language."""
        parser = get_parser(language="javascript")
        assert isinstance(parser, JavaScriptParser)

    def test_get_parser_from_filepath(self):
        """Test getting parser from file path."""
        parser = get_parser(filepath="test.py")
        assert isinstance(parser, PythonParser)

    def test_get_parser_language_takes_precedence(self):
        """Test that explicit language takes precedence over filepath."""
        parser = get_parser(language="javascript", filepath="test.py")
        assert isinstance(parser, JavaScriptParser)

    def test_get_parser_unknown_language(self):
        """Test that unknown language returns GenericParser."""
        parser = get_parser(language="unknown")
        assert isinstance(parser, GenericParser)

    def test_get_parser_no_args(self):
        """Test that no args returns GenericParser."""
        parser = get_parser()
        assert isinstance(parser, GenericParser)

    @pytest.mark.parametrize(
        "alias,expected_type",
        [
            ("py", PythonParser),
            ("js", JavaScriptParser),
            ("ts", TypeScriptParser),
            ("cs", CSharpParser),
            ("c#", CSharpParser),
            ("c++", CppParser),
        ],
    )
    def test_language_aliases(self, alias, expected_type):
        """Test language aliases."""
        parser = get_parser(language=alias)
        assert isinstance(parser, expected_type)
