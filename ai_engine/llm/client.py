"""Thin, decoupled wrapper around the LangChain chat model.

Deliberately does NOT import `app.core.config` (the backend's settings
system) so that `ai_engine` stays importable and testable in isolation from
`backend/`. We read the couple of env vars we need directly via `os.environ`.

Supported providers (set via ``LLM_PROVIDER`` env var):
  - ``anthropic`` (default) — requires ``langchain-anthropic``.
  - ``groq``                — requires ``langchain-groq`` (free tier available
                              at console.groq.com).

Every agent in `ai_engine.agents.*` is expected to work with or without an
LLM API key configured:
  - `is_llm_configured()` tells callers/agents which mode to run in.
  - `get_chat_model()` is only safe to call when `is_llm_configured()` is
    True; agents must still wrap the call site in try/except and fall back
    to their rule-based path on any failure (missing key, network error,
    rate limit, bad response, etc).
"""

from __future__ import annotations

import functools
import os

# Env vars checked for the API key, in order.
_ANTHROPIC_KEY_VARS = ("LLM_API_KEY", "ANTHROPIC_API_KEY")
_GROQ_KEY_VARS = ("LLM_API_KEY", "GROQ_API_KEY")

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5",
    "groq": "llama-3.3-70b-versatile",
}


# Tried in order when the configured Groq model is not available to the account
# (Groq retires models; access differs per account/tier).
_GROQ_PREFERRED_MODELS = (
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "llama-3.1-8b-instant",
)
_NON_CHAT_MARKERS = ("whisper", "tts", "guard", "orpheus", "playai", "embed", "safeguard")


@functools.lru_cache(maxsize=8)
def _resolve_groq_model(api_key: str, requested: str) -> str:
    """Return `requested` if the key can use it, else the best available chat model.

    One cheap models-list call per (key, model), cached for the process. If the
    list itself can't be fetched we keep `requested` and let the real call
    surface the actual error.
    """
    try:
        from groq import Groq

        available = {m.id for m in Groq(api_key=api_key).models.list().data}
    except Exception as exc:  # noqa: BLE001
        print(f"[ai_engine.llm] WARNING: could not list Groq models ({exc}); using '{requested}' as configured")
        return requested

    if requested in available:
        return requested
    for candidate in _GROQ_PREFERRED_MODELS:
        if candidate in available:
            print(f"[ai_engine.llm] WARNING: Groq model '{requested}' is not available to this key; using '{candidate}'")
            return candidate
    chat_models = sorted(m for m in available if not any(x in m for x in _NON_CHAT_MARKERS))
    if chat_models:
        print(f"[ai_engine.llm] WARNING: Groq model '{requested}' is not available; using '{chat_models[0]}'")
        return chat_models[0]
    return requested


def _get_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "anthropic").strip().lower()


def _get_api_key() -> str | None:
    provider = _get_provider()
    key_vars = _GROQ_KEY_VARS if provider == "groq" else _ANTHROPIC_KEY_VARS
    for var in key_vars:
        value = os.environ.get(var)
        if value:
            return value
    return None


def is_llm_configured() -> bool:
    """True iff an LLM API key env var is set for the configured provider."""
    return _get_api_key() is not None


def get_chat_model(temperature: float = 0.3, max_tokens: int = 1000):
    """Return a configured LangChain chat model instance.

    Provider is selected via ``LLM_PROVIDER`` env var (default: ``anthropic``).
    Model name comes from ``LLM_MODEL`` env var; falls back to a sensible
    default per provider.  API key is read from ``LLM_API_KEY`` (or the
    provider-specific fallback var).

    Raises if no API key is configured or the required package is unavailable
    — callers MUST check ``is_llm_configured()`` first and/or wrap this in
    try/except, per the module contract above.
    """
    provider = _get_provider()
    api_key = _get_api_key()

    if not api_key:
        raise RuntimeError(
            f"No LLM API key configured for provider '{provider}'. "
            "Set LLM_API_KEY (or ANTHROPIC_API_KEY / GROQ_API_KEY); "
            "callers should check is_llm_configured() before calling get_chat_model()."
        )

    default_model = DEFAULT_MODELS.get(provider, "llama-3.3-70b-versatile")
    model_name = os.environ.get("LLM_MODEL", default_model)

    if provider == "groq":
        from langchain_groq import ChatGroq  # optional dep: langchain-groq

        return ChatGroq(
            model=_resolve_groq_model(api_key, model_name), api_key=api_key, temperature=temperature, max_tokens=max_tokens,
            max_retries=1, timeout=45,
        )

    # Default: anthropic
    from langchain_anthropic import ChatAnthropic  # optional dep: langchain-anthropic

    return ChatAnthropic(model=model_name, api_key=api_key, temperature=temperature)
