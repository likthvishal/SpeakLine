"""Transcription module with pluggable backends for speech-to-text conversion."""

from abc import ABC, abstractmethod
from typing import Optional, Literal
import logging
import tempfile
import os

import numpy as np

logger = logging.getLogger(__name__)

WhisperModelSize = Literal["tiny", "base", "small", "medium", "large"]


class TranscriberError(Exception):
    """Base exception for transcription errors."""

    pass


class ModelNotFoundError(TranscriberError):
    """Error when transcription model is not found."""

    pass


class APIError(TranscriberError):
    """Error related to API calls."""

    pass


class TranscriberBase(ABC):
    """Abstract base class for transcription backends."""

    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio data to text.

        Args:
            audio: Audio data as numpy array of float32 values in [-1, 1] range.
            sample_rate: Sample rate of the audio data.

        Returns:
            Transcribed text.

        Raises:
            TranscriberError: If transcription fails.
        """
        pass


class WhisperTranscriber(TranscriberBase):
    """Transcriber using local OpenAI Whisper model."""

    def __init__(
        self,
        model_size: WhisperModelSize = "base",
        device: Optional[str] = None,
        language: Optional[str] = None,
    ) -> None:
        """Initialize the Whisper transcriber.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large).
            device: Device to run model on ('cpu', 'cuda', or None for auto).
            language: Language code for transcription (e.g., 'en'). None for auto-detect.
        """
        self._model_size = model_size
        self._device = device
        self._language = language
        self._model: Optional["whisper.Whisper"] = None

    def _load_model(self) -> "whisper.Whisper":
        """Load the Whisper model lazily."""
        if self._model is None:
            try:
                import whisper

                logger.info(f"Loading Whisper model: {self._model_size}")
                self._model = whisper.load_model(self._model_size, device=self._device)
                logger.info("Whisper model loaded successfully")
            except ImportError:
                raise ModelNotFoundError(
                    "openai-whisper is not installed. Install it with: pip install openai-whisper"
                )
            except Exception as e:
                raise TranscriberError(f"Failed to load Whisper model: {e}")
        return self._model

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio using local Whisper model.

        Args:
            audio: Audio data as numpy array.
            sample_rate: Sample rate of the audio.

        Returns:
            Transcribed text.

        Raises:
            TranscriberError: If transcription fails.
        """
        model = self._load_model()

        try:
            # Whisper expects float32 audio normalized to [-1, 1]
            audio = audio.astype(np.float32)

            # Resample if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                audio = self._resample(audio, sample_rate, 16000)

            # Transcribe
            options = {}
            if self._language:
                options["language"] = self._language

            result = model.transcribe(audio, **options)
            text = result["text"].strip()

            logger.info(f"Transcription complete: '{text[:50]}...' ({len(text)} chars)")

            return text

        except Exception as e:
            raise TranscriberError(f"Transcription failed: {e}")

    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        try:
            import scipy.signal

            num_samples = int(len(audio) * target_sr / orig_sr)
            return scipy.signal.resample(audio, num_samples).astype(np.float32)
        except ImportError:
            # Simple linear interpolation fallback
            ratio = target_sr / orig_sr
            indices = np.arange(0, len(audio), 1 / ratio)
            indices = np.clip(indices, 0, len(audio) - 1).astype(int)
            return audio[indices]


class OpenAITranscriber(TranscriberBase):
    """Transcriber using OpenAI Whisper API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-1",
        language: Optional[str] = None,
    ) -> None:
        """Initialize the OpenAI API transcriber.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            model: Model name to use (default: whisper-1).
            language: Language code for transcription.
        """
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._model = model
        self._language = language
        self._client: Optional["openai.OpenAI"] = None

        if not self._api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")

    def _get_client(self) -> "openai.OpenAI":
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                import openai

                if not self._api_key:
                    raise APIError("OpenAI API key is required")
                self._client = openai.OpenAI(api_key=self._api_key)
            except ImportError:
                raise TranscriberError(
                    "openai is not installed. Install it with: pip install openai"
                )
        return self._client

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio using OpenAI Whisper API.

        Args:
            audio: Audio data as numpy array.
            sample_rate: Sample rate of the audio.

        Returns:
            Transcribed text.

        Raises:
            TranscriberError: If transcription fails.
            APIError: If API call fails.
        """
        client = self._get_client()

        # Save audio to temporary WAV file (API requires file upload)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            self._save_wav(tmp_path, audio, sample_rate)

        try:
            with open(tmp_path, "rb") as audio_file:
                kwargs = {"model": self._model, "file": audio_file}
                if self._language:
                    kwargs["language"] = self._language

                response = client.audio.transcriptions.create(**kwargs)

            text = response.text.strip()
            logger.info(f"API transcription complete: '{text[:50]}...' ({len(text)} chars)")

            return text

        except Exception as e:
            raise APIError(f"OpenAI API transcription failed: {e}")
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _save_wav(self, path: str, audio: np.ndarray, sample_rate: int) -> None:
        """Save audio array to WAV file."""
        import wave

        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())


class MockTranscriber(TranscriberBase):
    """Mock transcriber for testing without actual transcription."""

    def __init__(self, fixed_text: Optional[str] = None) -> None:
        """Initialize mock transcriber.

        Args:
            fixed_text: Text to return for all transcriptions.
                If None, returns a default message.
        """
        self._fixed_text = fixed_text

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Return mock transcription.

        Args:
            audio: Audio data (ignored).
            sample_rate: Sample rate (ignored).

        Returns:
            Fixed mock text.
        """
        text = self._fixed_text or "This is a mock transcription for testing purposes"
        logger.info(f"Mock transcription: '{text}'")
        return text


def get_transcriber(
    backend: Literal["whisper", "openai", "mock"] = "whisper",
    **kwargs,
) -> TranscriberBase:
    """Factory function to get a transcriber instance.

    Args:
        backend: Transcription backend to use.
        **kwargs: Additional arguments passed to the transcriber.

    Returns:
        Transcriber instance.

    Raises:
        ValueError: If backend is not recognized.
    """
    transcribers = {
        "whisper": WhisperTranscriber,
        "openai": OpenAITranscriber,
        "mock": MockTranscriber,
    }

    if backend not in transcribers:
        raise ValueError(f"Unknown transcriber backend: {backend}. Use one of: {list(transcribers)}")

    return transcribers[backend](**kwargs)
