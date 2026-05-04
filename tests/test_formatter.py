"""Tests for the formatter module."""

import os

import pytest

from speakline.formatter import (
    FormatterBase,
    RuleBasedFormatter,
    PassthroughFormatter,
    LLMFormatter,
    get_formatter,
)


class TestRuleBasedFormatter:
    def test_inherits_from_base(self):
        assert isinstance(RuleBasedFormatter(), FormatterBase)

    def test_strips_filler_words(self):
        f = RuleBasedFormatter()
        result = f.format("uh this is um like the answer")
        assert "uh" not in result.lower().split()
        assert "um" not in result.lower().split()
        assert "like" not in result.lower().split()

    def test_capitalizes_first_letter(self):
        f = RuleBasedFormatter()
        assert f.format("compute factorial")[0].isupper()

    def test_empty_input_returns_empty(self):
        f = RuleBasedFormatter()
        assert f.format("") == ""
        assert f.format("   ") == ""

    def test_strips_trailing_period_for_single_sentence(self):
        f = RuleBasedFormatter()
        assert not f.format("compute factorial.").endswith(".")

    def test_preserves_camelcase_identifiers(self):
        """Bug fix: identifiers must not be lowercased."""
        f = RuleBasedFormatter()
        result = f.format("calls getUserById then parseJSON")
        assert "getUserById" in result
        assert "parseJSON" in result

    def test_preserves_pascalcase_identifiers(self):
        f = RuleBasedFormatter()
        result = f.format("instantiate UserAccount and call Save")
        assert "UserAccount" in result
        assert "Save" in result

    def test_preserves_snake_case_unchanged(self):
        f = RuleBasedFormatter()
        result = f.format("returns the user_id from db_session")
        assert "user_id" in result
        assert "db_session" in result

    def test_preserves_constants_uppercase(self):
        f = RuleBasedFormatter()
        result = f.format("compare against MAX_RETRIES limit")
        assert "MAX_RETRIES" in result

    def test_preserves_dotted_attribute_access(self):
        f = RuleBasedFormatter()
        result = f.format("calls self.userRepo.findOne with id")
        assert "self.userRepo.findOne" in result

    def test_filler_removal_is_case_insensitive(self):
        f = RuleBasedFormatter()
        result = f.format("UH this Is BASICALLY the answer")
        # Originals (UH/BASICALLY) should be gone, but 'Is' (real word) stays
        assert "UH" not in result
        assert "BASICALLY" not in result.upper().split()


class TestPassthroughFormatter:
    def test_returns_input_stripped(self):
        f = PassthroughFormatter()
        assert f.format("  hello  ") == "hello"

    def test_does_not_alter_case(self):
        f = PassthroughFormatter()
        assert f.format("getUserById") == "getUserById"


class TestLLMFormatterConfiguration:
    """LLMFormatter wiring (no actual API calls)."""

    @pytest.fixture(autouse=True)
    def _clear_env(self, monkeypatch):
        for k in (
            "SPEAKLINE_LLM_API_KEY",
            "SPEAKLINE_LLM_BASE_URL",
            "SPEAKLINE_LLM_MODEL",
            "OPENAI_API_KEY",
        ):
            monkeypatch.delenv(k, raising=False)

    def test_default_model_is_gpt_4o_mini(self):
        f = LLMFormatter(api_key="sk-test")
        assert f._model == "gpt-4o-mini"

    def test_explicit_model_override(self):
        f = LLMFormatter(api_key="sk-test", model="custom-model")
        assert f._model == "custom-model"

    def test_explicit_base_url_override(self):
        f = LLMFormatter(api_key="sk-test", base_url="https://example.com/v1")
        assert f._base_url == "https://example.com/v1"

    def test_env_var_model(self, monkeypatch):
        monkeypatch.setenv("SPEAKLINE_LLM_MODEL", "anthropic/claude-haiku-4-5")
        f = LLMFormatter(api_key="sk-test")
        assert f._model == "anthropic/claude-haiku-4-5"

    def test_env_var_base_url(self, monkeypatch):
        monkeypatch.setenv("SPEAKLINE_LLM_BASE_URL", "https://openrouter.ai/api/v1")
        f = LLMFormatter(api_key="sk-test")
        assert f._base_url == "https://openrouter.ai/api/v1"

    def test_speakline_api_key_takes_precedence_over_openai(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
        monkeypatch.setenv("SPEAKLINE_LLM_API_KEY", "sk-speakline")
        f = LLMFormatter()
        assert f._api_key == "sk-speakline"

    def test_falls_back_to_openai_api_key(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
        f = LLMFormatter()
        assert f._api_key == "sk-openai"

    def test_explicit_arg_beats_env(self, monkeypatch):
        monkeypatch.setenv("SPEAKLINE_LLM_MODEL", "from-env")
        f = LLMFormatter(api_key="sk-test", model="from-arg")
        assert f._model == "from-arg"


class TestGetFormatter:
    def test_get_rules(self):
        assert isinstance(get_formatter("rules"), RuleBasedFormatter)

    def test_get_passthrough(self):
        assert isinstance(get_formatter("none"), PassthroughFormatter)

    def test_get_llm(self):
        # api_key passed through kwargs; no API call until format()
        f = get_formatter("llm", api_key="sk-test")
        assert isinstance(f, LLMFormatter)

    def test_invalid_backend(self):
        with pytest.raises(ValueError, match="Unknown formatter backend"):
            get_formatter("nope")

    def test_default_is_rules(self):
        assert isinstance(get_formatter(), RuleBasedFormatter)
