"""Comment formatter — cleans raw transcription into idiomatic code comments.

Sits between transcription and insertion. Transforms verbose, filler-laden
speech ("uh this function basically like takes the input and then returns
the factorial recursively") into concise code comments ("Recursively computes
factorial of n").

Supports multiple backends:
- OpenAI API (GPT-3.5/4) — best quality
- Local rule-based — no API needed, decent quality
"""

from abc import ABC, abstractmethod
from typing import Optional, Literal
import logging
import os
import re

logger = logging.getLogger(__name__)


class FormatterError(Exception):
    """Base exception for formatter errors."""
    pass


class FormatterBase(ABC):
    """Abstract base class for comment formatters."""

    @abstractmethod
    def format(self, raw_text: str, context: Optional[str] = None) -> str:
        """Format raw transcription into a clean code comment.

        Args:
            raw_text: Raw transcription output from Whisper/OpenAI.
            context: Optional surrounding code context for better formatting.

        Returns:
            Cleaned, concise comment text.
        """
        pass


class RuleBasedFormatter(FormatterBase):
    """Rule-based formatter that cleans transcription without an LLM.

    Removes filler words, normalizes punctuation, and condenses phrasing.
    Good enough for simple comments; no API key needed.
    """

    FILLER_WORDS = [
        r"\buh+\b", r"\bum+\b", r"\blike\b", r"\byou know\b",
        r"\bbasically\b", r"\bactually\b", r"\bso\b", r"\bjust\b",
        r"\bkind of\b", r"\bsort of\b", r"\bi mean\b", r"\bright\b",
        r"\bokay so\b", r"\bwell\b", r"\bi think\b", r"\bi guess\b",
        r"\bliterally\b",
    ]

    PHRASE_REPLACEMENTS = [
        (r"\bthis function\b", ""),
        (r"\bthis method\b", ""),
        (r"\bwhat this does is\b", ""),
        (r"\bwhat it does is\b", ""),
        (r"\band then\b", ","),
        (r"\band also\b", ","),
    ]

    def format(self, raw_text: str, context: Optional[str] = None) -> str:
        text = raw_text.strip()
        if not text:
            return text

        text = text.lower()

        # Remove filler words
        for pattern in self.FILLER_WORDS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Apply phrase replacements
        for pattern, replacement in self.PHRASE_REPLACEMENTS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Remove leading/trailing commas
        text = text.strip(",").strip()

        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]

        # Remove trailing period if it's a short comment (single sentence)
        if text.endswith(".") and text.count(".") == 1:
            text = text[:-1]

        return text


class LLMFormatter(FormatterBase):
    """LLM-powered formatter using OpenAI API.

    Transforms raw speech into idiomatic, concise code comments.
    Uses GPT-3.5-turbo by default (fast, cheap, good enough).
    """

    SYSTEM_PROMPT = (
        "You are a code comment formatter. You receive raw speech transcriptions "
        "from a developer speaking about their code. Your job is to transform the "
        "raw speech into a clean, concise, idiomatic code comment.\n\n"
        "Rules:\n"
        "- Remove ALL filler words (uh, um, like, basically, you know, etc.)\n"
        "- Condense verbose explanations into concise technical descriptions\n"
        "- Use imperative mood when possible (e.g., 'Compute factorial' not 'This computes factorial')\n"
        "- Keep it to one sentence unless the explanation genuinely requires more\n"
        "- Do NOT add code, markdown, or comment syntax (no #, //, etc.)\n"
        "- Do NOT add quotes around the output\n"
        "- Preserve technical terms and variable/function names mentioned\n"
        "- Output ONLY the cleaned comment text, nothing else"
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
                if not self._api_key:
                    raise FormatterError(
                        "OpenAI API key required for LLM formatter. "
                        "Set OPENAI_API_KEY env var or pass api_key."
                    )
                self._client = openai.OpenAI(api_key=self._api_key)
            except ImportError:
                raise FormatterError("openai package required: pip install openai")
        return self._client

    def format(self, raw_text: str, context: Optional[str] = None) -> str:
        if not raw_text.strip():
            return raw_text

        client = self._get_client()

        user_msg = f"Raw transcription: {raw_text}"
        if context:
            user_msg += f"\n\nSurrounding code context:\n{context}"

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            result = response.choices[0].message.content.strip()
            # Strip quotes if LLM wraps output
            if (result.startswith('"') and result.endswith('"')) or \
               (result.startswith("'") and result.endswith("'")):
                result = result[1:-1]
            logger.info(f"LLM formatted: '{raw_text[:40]}...' -> '{result[:40]}...'")
            return result
        except Exception as e:
            logger.warning(f"LLM formatting failed, falling back to rule-based: {e}")
            return RuleBasedFormatter().format(raw_text, context)


class PassthroughFormatter(FormatterBase):
    """No-op formatter — returns raw transcription unchanged."""

    def format(self, raw_text: str, context: Optional[str] = None) -> str:
        return raw_text.strip()


def get_formatter(
    backend: Literal["llm", "rules", "none"] = "rules",
    **kwargs,
) -> FormatterBase:
    """Factory function to get a formatter instance.

    Args:
        backend: Formatter backend — 'llm' (OpenAI), 'rules' (local), 'none' (passthrough).
        **kwargs: Additional arguments passed to the formatter.

    Returns:
        Formatter instance.
    """
    formatters = {
        "llm": LLMFormatter,
        "rules": RuleBasedFormatter,
        "none": PassthroughFormatter,
    }

    if backend not in formatters:
        raise ValueError(
            f"Unknown formatter backend: {backend}. Use one of: {list(formatters)}"
        )

    cls = formatters[backend]
    if cls is LLMFormatter:
        return cls(**kwargs)
    return cls()
