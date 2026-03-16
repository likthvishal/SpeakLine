"""Tests for the commenter module."""

import tempfile
import os

import pytest

from voicecomment.commenter import VoiceCommenter, VoiceCommenterError
from voicecomment.recorder import MockRecorder
from voicecomment.transcriber import MockTranscriber


class TestVoiceCommenter:
    """Tests for VoiceCommenter class."""

    @pytest.fixture
    def commenter(self):
        """Create a VoiceCommenter with mock components."""
        return VoiceCommenter(
            recorder=MockRecorder(),
            transcriber=MockTranscriber(fixed_text="Test comment"),
        )

    @pytest.fixture
    def temp_python_file(self):
        """Create a temporary Python file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("def hello():\n    print('Hello, World!')\n")
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_init_with_defaults(self):
        """Test initialization with mock components."""
        commenter = VoiceCommenter(
            recorder=MockRecorder(),
            transcriber=MockTranscriber(),
        )
        assert commenter.recorder is not None
        assert commenter.transcriber is not None

    def test_language_property(self):
        """Test language property getter and setter."""
        commenter = VoiceCommenter(
            language="python",
            recorder=MockRecorder(),
            transcriber=MockTranscriber(),
        )
        assert commenter.language == "python"

        commenter.language = "javascript"
        assert commenter.language == "javascript"

    def test_insert_comment_to_string(self, commenter):
        """Test inserting comment into code string."""
        code = "def foo():\n    pass"
        result = commenter.insert_comment_to_string(
            code=code,
            comment="This is a function",
            line_number=1,
            language="python",
        )
        assert "# This is a function" in result
        assert "def foo():" in result

    def test_insert_comment_to_string_preserves_code(self, commenter):
        """Test that insert_comment_to_string preserves original code."""
        code = "line1\nline2\nline3"
        result = commenter.insert_comment_to_string(
            code=code,
            comment="My comment",
            line_number=2,
            language="python",
        )
        lines = result.split("\n")
        assert "line1" in lines
        assert "line2" in lines
        assert "line3" in lines
        assert len(lines) == 4  # Original 3 + 1 comment

    def test_insert_comment_to_file(self, commenter, temp_python_file):
        """Test inserting comment into file."""
        commenter.insert_comment_to_file(
            filepath=temp_python_file,
            comment="This function says hello",
            line_number=1,
        )

        with open(temp_python_file, "r") as f:
            content = f.read()

        assert "# This function says hello" in content
        assert "def hello():" in content

    def test_insert_comment_to_file_not_found(self, commenter):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            commenter.insert_comment_to_file(
                filepath="/nonexistent/path/file.py",
                comment="Test",
                line_number=1,
            )

    def test_record_and_insert(self, commenter, temp_python_file):
        """Test full record and insert workflow."""
        result = commenter.record_and_insert(
            filepath=temp_python_file,
            line_number=1,
            duration=0.5,
        )

        assert result == "Test comment"

        with open(temp_python_file, "r") as f:
            content = f.read()

        assert "# Test comment" in content

    def test_record_and_insert_file_not_found(self, commenter):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            commenter.record_and_insert(
                filepath="/nonexistent/path/file.py",
                line_number=1,
            )

    def test_transcribe_only(self, commenter):
        """Test transcribe-only mode."""
        result = commenter.transcribe_only(duration=0.5)
        assert result == "Test comment"

    def test_transcribe_only_returns_transcription(self):
        """Test that transcribe_only returns the transcription."""
        custom_text = "This is my voice comment"
        commenter = VoiceCommenter(
            recorder=MockRecorder(),
            transcriber=MockTranscriber(fixed_text=custom_text),
        )

        result = commenter.transcribe_only(duration=0.5)
        assert result == custom_text

    def test_insert_comment_with_indentation(self, commenter):
        """Test that comments respect indentation."""
        code = "class Foo:\n    def bar(self):\n        return 42"
        result = commenter.insert_comment_to_string(
            code=code,
            comment="Return value",
            line_number=3,
            language="python",
        )

        lines = result.split("\n")
        # The comment should be indented to match the return statement
        comment_line = [l for l in lines if "Return value" in l][0]
        assert comment_line.startswith("        #")

    def test_different_languages(self):
        """Test comment insertion with different languages."""
        commenter = VoiceCommenter(
            recorder=MockRecorder(),
            transcriber=MockTranscriber(fixed_text="Test"),
        )
        code = "function test() {\n    return true;\n}"

        # JavaScript uses //
        result = commenter.insert_comment_to_string(
            code=code,
            comment="Returns true",
            line_number=2,
            language="javascript",
        )
        assert "// Returns true" in result

        # Python uses #
        py_code = "def test():\n    return True"
        result = commenter.insert_comment_to_string(
            code=py_code,
            comment="Returns True",
            line_number=2,
            language="python",
        )
        assert "# Returns True" in result


class TestVoiceCommenterWithEmptyTranscription:
    """Tests for handling empty transcriptions."""

    def test_empty_transcription_raises_error(self):
        """Test that empty transcription raises VoiceCommenterError."""
        commenter = VoiceCommenter(
            recorder=MockRecorder(),
            transcriber=MockTranscriber(fixed_text="   "),  # Whitespace only
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("code = 1\n")
            temp_path = f.name

        try:
            with pytest.raises(VoiceCommenterError, match="empty text"):
                commenter.record_and_insert(temp_path, 1, duration=0.5)
        finally:
            os.unlink(temp_path)
