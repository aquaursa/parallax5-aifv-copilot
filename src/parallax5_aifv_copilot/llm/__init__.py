"""LLM provider adapters for the AI-FV Co-Pilot.

Four providers are supported: Anthropic, OpenAI, Deepseek, Mistral.
Each speaks the same LLMClient protocol; the benchmark harness iterates
over them identically.
"""
from __future__ import annotations

from typing import Literal

from .base import LLMClient, LLMResponse, hash_text
from .claude import ClaudeClient
from .deepseek import DeepseekClient
from .mistral import MistralClient
from .openai import OpenAIClient

Provider = Literal["anthropic", "openai", "deepseek", "mistral"]

DEFAULT_MODELS: dict[Provider, str] = {
    "anthropic": "claude-opus-4-7",
    "openai":    "gpt-5.5-pro",
    "deepseek":  "deepseek-v4-pro",
    "mistral":   "labs-leanstral-2603",
}


def make_client(provider: Provider, model: str | None = None) -> LLMClient:
    """Construct a client for the named provider."""
    m = model or DEFAULT_MODELS[provider]
    if provider == "anthropic":
        return ClaudeClient(model=m)
    if provider == "openai":
        return OpenAIClient(model=m)
    if provider == "deepseek":
        return DeepseekClient(model=m)
    if provider == "mistral":
        return MistralClient(model=m)
    raise ValueError(f"Unknown provider: {provider}")


def make_all_default_clients() -> dict[Provider, LLMClient]:
    """Construct one client per provider with the default-pinned model."""
    return {p: make_client(p) for p in DEFAULT_MODELS}


__all__ = [
    "LLMClient",
    "LLMResponse",
    "Provider",
    "DEFAULT_MODELS",
    "make_client",
    "make_all_default_clients",
    "hash_text",
]
