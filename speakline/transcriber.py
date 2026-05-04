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


def _resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio to ``target_sr``. Uses scipy when available, else linear interp."""
    if orig_sr == target_sr:
        return audio.astype(np.float32)
    try:
        import scipy.signal

        num_samples = int(len(audio) * target_sr / orig_sr)
        return scipy.signal.resample(audio, num_samples).astype(np.float32)
    except ImportError:
        ratio = target_sr / orig_sr
        indices = np.arange(0, len(audio), 1 / ratio)
        indices = np.clip(indices, 0, len(audio) - 1).astype(int)
        return audio[indices].astype(np.float32)


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
        return _resample(audio, orig_sr, target_sr)


class FasterWhisperTranscriber(TranscriberBase):
    """Transcriber using faster-whisper (CTranslate2 backend).

    Drop-in alternative to ``WhisperTranscriber`` that runs the same
    Whisper models 4-10x faster with significantly lower memory usage.
    Requires ``pip install faster-whisper``.
    """

    def __init__(
        self,
        model_size: WhisperModelSize = "base",
        device: str = "auto",
        compute_type: str = "default",
        language: Optional[str] = None,
    ) -> None:
        """Initialize the faster-whisper transcriber.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large).
            device: Device for inference ('cpu', 'cuda', 'auto').
            compute_type: Quantization mode ('default', 'int8', 'int8_float16',
                'float16', 'float32'). 'int8' is fastest on CPU.
            language: Language code (e.g., 'en'). None for auto-detect.
        """
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._language = language
        self._model: Optional["faster_whisper.WhisperModel"] = None

    def _load_model(self) -> "faster_whisper.WhisperModel":
        if self._model is None:
            try:
                from faster_whisper import WhisperModel

                logger.info(f"Loading faster-whisper model: {self._model_size}")
                self._model = WhisperModel(
                    self._model_size,
                    device=self._device,
                    compute_type=self._compute_type,
                )
                logger.info("faster-whisper model loaded")
            except ImportError:
                raise ModelNotFoundError(
                    "faster-whisper is not installed. Install it with: "
                    "pip install faster-whisper  (or: pip install speakline[fast])"
                )
            except Exception as e:
                raise TranscriberError(f"Failed to load faster-whisper model: {e}")
        return self._model

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        model = self._load_model()

        try:
            audio = audio.astype(np.float32)
            if sample_rate != 16000:
                audio = _resample(audio, sample_rate, 16000)

            kwargs = {}
            if self._language:
                kwargs["language"] = self._language

            segments, _info = model.transcribe(audio, **kwargs)
            text = "".join(seg.text for seg in segments).strip()

            logger.info(f"faster-whisper transcription: '{text[:50]}...' ({len(text)} chars)")
            return text

        except Exception as e:
            raise TranscriberError(f"faster-whisper transcription failed: {e}")


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
        # Use delete=True with context manager for secure cleanup
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_file:
                tmp_path = tmp_file.name
                self._save_wav(tmp_path, audio, sample_rate)

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
    backend: Literal["whisper", "faster-whisper", "openai", "mock"] = "whisper",
    **kwargs,
) -> TranscriberBase:
    """Factory function to get a transcriber instance.

    Args:
        backend: Transcription backend — 'whisper' (local openai-whisper),
            'faster-whisper' (CTranslate2, 4-10x faster), 'openai' (API),
            or 'mock' (testing).
        **kwargs: Additional arguments passed to the transcriber.

    Returns:
        Transcriber instance.

    Raises:
        ValueError: If backend is not recognized.
    """
    transcribers = {
        "whisper": WhisperTranscriber,
        "faster-whisper": FasterWhisperTranscriber,
        "openai": OpenAITranscriber,
        "mock": MockTranscriber,
    }

    if backend not in transcribers:
        raise ValueError(f"Unknown transcriber backend: {backend}. Use one of: {list(transcribers)}")

    return transcribers[backend](**kwargs)
