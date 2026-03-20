"""Audio recording module with local microphone support and silence detection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import logging
import time

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Configuration for audio recording.

    Attributes:
        sample_rate: Audio sample rate in Hz (default: 16000 for Whisper compatibility)
        channels: Number of audio channels (default: 1 for mono)
        chunk_size: Number of frames per buffer (default: 1024)
        format_width: Sample width in bytes (default: 2 for 16-bit audio)
    """

    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format_width: int = 2


@dataclass
class SilenceConfig:
    """Configuration for silence detection.

    Attributes:
        threshold: Amplitude threshold below which audio is considered silence (0-1 range)
        duration: Duration in seconds of silence required to stop recording
        min_recording_duration: Minimum recording duration before silence detection kicks in
    """

    threshold: float = 0.01
    duration: float = 2.0
    min_recording_duration: float = 1.0


class RecorderError(Exception):
    """Base exception for recorder errors."""

    pass


class AudioDeviceError(RecorderError):
    """Error related to audio device access."""

    pass


class RecorderBase(ABC):
    """Abstract base class for audio recorders."""

    @abstractmethod
    def record(
        self,
        duration: Optional[float] = None,
        silence_detection: bool = True,
    ) -> np.ndarray:
        """Record audio from the input device.

        Args:
            duration: Fixed recording duration in seconds. If None, uses silence detection.
            silence_detection: Whether to use silence detection to stop recording.
                Only applies when duration is None.

        Returns:
            Audio data as a numpy array of float32 values normalized to [-1, 1].

        Raises:
            RecorderError: If recording fails.
        """
        pass

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Return the sample rate of recorded audio."""
        pass


class LocalAudioRecorder(RecorderBase):
    """Records audio from the local system microphone using PyAudio."""

    def __init__(
        self,
        config: Optional[AudioConfig] = None,
        silence_config: Optional[SilenceConfig] = None,
    ) -> None:
        """Initialize the local audio recorder.

        Args:
            config: Audio configuration. Uses defaults if not provided.
            silence_config: Silence detection configuration. Uses defaults if not provided.
        """
        self._config = config or AudioConfig()
        self._silence_config = silence_config or SilenceConfig()
        self._pyaudio: Optional["pyaudio.PyAudio"] = None

    def _get_pyaudio(self) -> "pyaudio.PyAudio":
        """Get or create PyAudio instance."""
        if self._pyaudio is None:
            try:
                import pyaudio

                self._pyaudio = pyaudio.PyAudio()
            except ImportError:
                raise RecorderError(
                    "PyAudio is not installed. Install it with: pip install pyaudio"
                )
            except Exception as e:
                raise AudioDeviceError(f"Failed to initialize PyAudio: {e}")
        return self._pyaudio

    def _get_format(self) -> int:
        """Get PyAudio format constant based on format width."""
        import pyaudio

        format_map = {
            1: pyaudio.paInt8,
            2: pyaudio.paInt16,
            4: pyaudio.paInt32,
        }
        return format_map.get(self._config.format_width, pyaudio.paInt16)

    def _is_silent(self, audio_chunk: np.ndarray) -> bool:
        """Check if an audio chunk is silent based on amplitude threshold."""
        if len(audio_chunk) == 0:
            return True
        amplitude = np.abs(audio_chunk).mean()
        return amplitude < self._silence_config.threshold

    def record(
        self,
        duration: Optional[float] = None,
        silence_detection: bool = True,
    ) -> np.ndarray:
        """Record audio from the microphone.

        Args:
            duration: Fixed recording duration in seconds. If None and silence_detection
                is True, recording stops after detecting silence.
            silence_detection: Whether to use silence detection. Ignored if duration is set.

        Returns:
            Audio data as numpy array of float32 values in [-1, 1] range.

        Raises:
            RecorderError: If recording fails.
            AudioDeviceError: If audio device is not available.
        """
        import pyaudio

        pa = self._get_pyaudio()
        stream = None

        try:
            stream = pa.open(
                format=self._get_format(),
                channels=self._config.channels,
                rate=self._config.sample_rate,
                input=True,
                frames_per_buffer=self._config.chunk_size,
            )
        except Exception as e:
            raise AudioDeviceError(f"Failed to open audio stream: {e}")

        frames: list[bytes] = []
        silence_start: Optional[float] = None
        recording_start = time.time()

        logger.info("Recording started...")

        try:
            while True:
                try:
                    data = stream.read(self._config.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    logger.warning(f"Error reading audio chunk: {e}")
                    continue

                elapsed = time.time() - recording_start

                # Fixed duration mode
                if duration is not None:
                    if elapsed >= duration:
                        logger.info(f"Recording completed (fixed duration: {duration}s)")
                        break
                    continue

                # Silence detection mode
                if silence_detection and elapsed >= self._silence_config.min_recording_duration:
                    # Convert chunk to numpy for amplitude check
                    chunk_array = self._bytes_to_numpy(data)

                    if self._is_silent(chunk_array):
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start >= self._silence_config.duration:
                            logger.info("Silence detected, stopping recording")
                            break
                    else:
                        silence_start = None

        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.warning(f"Error closing audio stream: {e}")

        # Convert all frames to numpy array
        audio_data = b"".join(frames)
        audio_array = self._bytes_to_numpy(audio_data)

        logger.info(f"Recording complete: {len(audio_array) / self._config.sample_rate:.2f}s")

        return audio_array

    def _bytes_to_numpy(self, data: bytes) -> np.ndarray:
        """Convert raw audio bytes to normalized float32 numpy array."""
        dtype_map = {
            1: np.int8,
            2: np.int16,
            4: np.int32,
        }
        dtype = dtype_map.get(self._config.format_width, np.int16)
        max_val = np.iinfo(dtype).max

        audio_array = np.frombuffer(data, dtype=dtype).astype(np.float32)
        audio_array = audio_array / max_val  # Normalize to [-1, 1]

        return audio_array

    @property
    def sample_rate(self) -> int:
        """Return the configured sample rate."""
        return self._config.sample_rate

    def __del__(self) -> None:
        """Clean up PyAudio instance."""
        if self._pyaudio is not None:
            self._pyaudio.terminate()


class MockRecorder(RecorderBase):
    """Mock recorder for testing without audio hardware."""

    def __init__(
        self,
        config: Optional[AudioConfig] = None,
        mock_duration: float = 1.0,
    ) -> None:
        """Initialize mock recorder.

        Args:
            config: Audio configuration.
            mock_duration: Duration of mock audio to generate.
        """
        self._config = config or AudioConfig()
        self._mock_duration = mock_duration

    def record(
        self,
        duration: Optional[float] = None,
        silence_detection: bool = True,
    ) -> np.ndarray:
        """Generate mock audio data.

        Args:
            duration: Recording duration (uses mock_duration if not specified).
            silence_detection: Ignored for mock recorder.

        Returns:
            Mock audio data as numpy array.
        """
        actual_duration = duration or self._mock_duration
        num_samples = int(actual_duration * self._config.sample_rate)

        # Generate some noise that looks like speech
        t = np.linspace(0, actual_duration, num_samples)
        audio = np.sin(2 * np.pi * 440 * t) * 0.3  # 440Hz tone
        audio += np.random.normal(0, 0.1, num_samples)  # Add noise
        audio = np.clip(audio, -1, 1).astype(np.float32)

        logger.info(f"Mock recording generated: {actual_duration}s")

        return audio

    @property
    def sample_rate(self) -> int:
        """Return the configured sample rate."""
        return self._config.sample_rate
