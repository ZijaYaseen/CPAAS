"""LLM model provider for the OpenAI Agents SDK.

Uses any OpenAI-compatible endpoint. Default config points at Google Gemini's
OpenAI-compatible API (the Panaversity pattern): an ``AsyncOpenAI`` client with
Gemini's base_url + API key, wrapped in ``OpenAIChatCompletionsModel``. OpenAI
platform tracing is disabled (we don't have an OpenAI key).
"""

from functools import lru_cache

from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

from src.core.config import settings

# No OpenAI key → turn off the SDK's tracing exporter (avoids noisy 401s).
if settings.llm_tracing_disabled:
    set_tracing_disabled(True)


@lru_cache
def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url or None,
    )


def get_chat_model() -> OpenAIChatCompletionsModel:
    """Return the configured chat model (e.g. a Gemini model via OpenAI-compat)."""
    return OpenAIChatCompletionsModel(model=settings.llm_model, openai_client=_client())
