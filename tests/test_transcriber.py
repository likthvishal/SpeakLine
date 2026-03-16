"""Tests for the transcriber module."""

import numpy as np
import pytest

from voicecomment.transcriber import (
    TranscriberBase,
    MockTranscriber,
    get_transcriber,
)


class TestMockTranscriber:
    """Tests for MockTranscriber class."""

    def test_inherits_from_base(self):
        """Test that MockTranscriber inherits from TranscriberBase."""
        transcriber = MockTranscriber()
        assert isinstance(transcriber, TranscriberBase)

    def test_transcribe_returns_string(self):
        """Test that transcribe returns a string."""
        transcriber = MockTranscriber()
        audio = np.zeros(16000, dtype=np.float32)
        result = transcriber.transcribe(audio)
        assert isinstance(result, str)

    def test_transcribe_default_text(self):
        """Test default transcription text."""
        transcriber = MockTranscriber()
        audio = np.zeros(16000, dtype=np.float32)
        result = transcriber.transcribe(audio)
        assert "mock transcription" in result.lower()

    def test_transcribe_fixed_text(self):
        """Test custom fixed transcription text."""
        custom_text = "This is my custom comment"
        transcriber = MockTranscriber(fixed_text=custom_text)
        audio = np.zeros(16000, dtype=np.float32)
        result = transcriber.transcribe(audio)
        assert result == custom_text

    def test_transcribe_ignores_audio_content(self):
        """Test that MockTranscriber ignores actual audio content."""
        transcriber = MockTranscriber(fixed_text="Fixed")

        # Different audio inputs should give same result
        audio1 = np.zeros(16000, dtype=np.float32)
        audio2 = np.ones(16000, dtype=np.float32)
        audio3 = np.random.randn(16000).astype(np.float32)

        assert transcriber.transcribe(audio1) == "Fixed"
        assert transcriber.transcribe(audio2) == "Fixed"
        assert transcriber.transcribe(audio3) == "Fixed"


class TestGetTranscriber:
    """Tests for get_transcriber factory function."""

    def test_get_mock_transcriber(self):
        """Test getting mock transcriber."""
        transcriber = get_transcriber("mock")
        assert isinstance(transcriber, MockTranscriber)

    def test_get_mock_with_kwargs(self):
        """Test getting mock transcriber with kwargs."""
        transcriber = get_transcriber("mock", fixed_text="Custom")
        assert isinstance(transcriber, MockTranscriber)
        audio = np.zeros(16000, dtype=np.float32)
        assert transcriber.transcribe(audio) == "Custom"

    def test_invalid_backend(self):
        """Test that invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Unknown transcriber backend"):
            get_transcriber("invalid_backend")
