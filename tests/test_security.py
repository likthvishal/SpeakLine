# tests/test_security.py
import pytest
import tempfile
import os
from voicecomment import VoiceCommenter, VoiceCommenterError

class TestSecurityVulnerabilities:
    """Test fixes for security vulnerabilities."""

    def test_path_traversal_blocked(self):
        """Reject attempts to write outside of intended directory."""
        commenter = VoiceCommenter()

        # Test various path traversal attempts
        dangerous_paths = [
            "/etc/passwd",
            "C:\\Windows\\System32\\test.py",
            "/sys/kernel/config",
        ]

        for path in dangerous_paths:
            with pytest.raises(VoiceCommenterError, match="Cannot modify system files"):
                commenter._validate_filepath(path)

    def test_null_byte_in_path_rejected(self):
        """Reject paths with null bytes."""
        commenter = VoiceCommenter()

        with pytest.raises(VoiceCommenterError, match="null bytes"):
            commenter._validate_filepath("file\x00.py")

    def test_invalid_line_number_type(self):
        """Reject non-integer line numbers."""
        commenter = VoiceCommenter()

        # Test with string-type line numbers
        with pytest.raises(Exception, match="must be an integer"):
            commenter.insert_comment_to_string("x = 1", "comment", "1")

        # Test with float line numbers
        with pytest.raises(Exception, match="must be an integer"):
            commenter.insert_comment_to_string("x = 1", "comment", 1.5)

    def test_file_encoding_fallback(self):
        """Handle non-UTF-8 encoded files gracefully."""
        commenter = VoiceCommenter()

        # Create a temp file with latin-1 encoding
        temp_fd, temp_path = tempfile.mkstemp(suffix=".py")
        try:
            # Write latin-1 encoded content directly to fd
            os.write(temp_fd, "# café\nx = 1\n".encode("latin-1"))
            os.close(temp_fd)

            # Should not crash, should fallback to latin-1
            commenter.insert_comment_to_file(temp_path, "new comment", 2)

            # Verify it was written
            with open(temp_path, "rb") as verify:
                content = verify.read()
                assert b"new comment" in content
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def test_atomic_write_on_error(self):
        """Verify atomic writes don't corrupt file on error."""
        commenter = VoiceCommenter()

        # Create temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".py")
        try:
            # Write original content
            original = "x = 1\ny = 2\nz = 3\n"
            os.write(temp_fd, original.encode("utf-8"))
            os.close(temp_fd)

            # Insert valid comment
            commenter.insert_comment_to_file(temp_path, "valid comment", 2)

            # Verify original content is still there, plus new comment
            with open(temp_path, "r") as verify:
                content = verify.read()
                assert "valid comment" in content
                assert "y = 2" in content  # Original content intact
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])