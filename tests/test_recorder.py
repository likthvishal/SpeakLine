"""Tests for the recorder module."""

import numpy as np
import pytest

from speakline.recorder import (
    AudioConfig,
    SilenceConfig,
    MockRecorder,
    RecorderBase,
)


class TestAudioConfig:
    """Tests for AudioConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AudioConfig()
        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.chunk_size == 1024
        assert config.format_width == 2

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AudioConfig(
            sample_rate=44100,
            channels=2,
            chunk_size=2048,
            format_width=4,
        )
        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.chunk_size == 2048
        assert config.format_width == 4


class TestSilenceConfig:
    """Tests for SilenceConfig dataclass."""

    def test_default_values(self):
        """Test default silence detection values."""
        config = SilenceConfig()
        assert config.threshold == 0.03
        assert config.duration == 3.0
        assert config.min_recording_duration == 3.0


class TestMockRecorder:
    """Tests for MockRecorder class."""

    def test_inherits_from_base(self):
        """Test that MockRecorder inherits from RecorderBase."""
        recorder = MockRecorder()
        assert isinstance(recorder, RecorderBase)

    def test_record_returns_numpy_array(self):
        """Test that record returns a numpy array."""
        recorder = MockRecorder()
        audio = recorder.record(duration=1.0)
        assert isinstance(audio, np.ndarray)

    def test_record_duration(self):
        """Test that record respects duration parameter."""
        config = AudioConfig(sample_rate=16000)
        recorder = MockRecorder(config=config, mock_duration=1.0)

        # Fixed duration
        audio = recorder.record(duration=2.0)
        expected_samples = 2.0 * config.sample_rate
        assert len(audio) == int(expected_samples)

    def test_record_default_duration(self):
        """Test that record uses mock_duration when no duration specified."""
        config = AudioConfig(sample_rate=16000)
        recorder = MockRecorder(config=config, mock_duration=0.5)

        audio = recorder.record()
        expected_samples = 0.5 * config.sample_rate
        assert len(audio) == int(expected_samples)

    def test_sample_rate_property(self):
        """Test sample_rate property."""
        config = AudioConfig(sample_rate=44100)
        recorder = MockRecorder(config=config)
        assert recorder.sample_rate == 44100

    def test_audio_values_normalized(self):
        """Test that audio values are in [-1, 1] range."""
        recorder = MockRecorder()
        audio = recorder.record(duration=1.0)
        assert audio.min() >= -1.0
        assert audio.max() <= 1.0

    def test_audio_is_float32(self):
        """Test that audio is float32 dtype."""
        recorder = MockRecorder()
        audio = recorder.record(duration=1.0)
        assert audio.dtype == np.float32
