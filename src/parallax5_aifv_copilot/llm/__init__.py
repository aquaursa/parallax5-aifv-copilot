"""LLM provider adapters for the AI-FV Co-Pilot.

Four providers are supported: Anthropic, OpenAI, Deepseek, Mistral.
Each speaks the same LLMClient protocol; the benchmark harness iterates
over them identically.

The Anthropic adapter has TWO implementations:
  - ClaudeClient: makes API calls when ANTHROPIC_API_KEY is set.
  - ClaudeSelfHostClient: reads from a deterministic on-disk cache
    when the benchmark operator IS Claude (no separate API key needed).
The factory `make_client("anthropic", ...)` picks the right one based on
environment.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from .base import LLMClient, LLMResponse, hash_text
from .claude import ClaudeClient
from .claude_selfhost import ClaudeSelfHostClient
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

ANTHROPIC_CACHE_DIR = Path("results/anthropic_cache")


def make_client(
    provider: Provider,
    model: str | None = None,
    *,
    anthropic_cache_dir: Path | None = None,
) -> LLMClient:
    """Construct a client for the named provider.

    For Anthropic, if ANTHROPIC_API_KEY is set in the environment the
    real ClaudeClient is used. Otherwise a ClaudeSelfHostClient
    backed by `anthropic_cache_dir` (default: results/anthropic_cache/)
    is used — the operator must prime the cache before benchmark runs.
    """
    m = model or DEFAULT_MODELS[provider]
    if provider == "anthropic":
        if os.environ.get("ANTHROPIC_API_KEY"):
            return ClaudeClient(model=m)
        return ClaudeSelfHostClient(
            cache_dir=anthropic_cache_dir or ANTHROPIC_CACHE_DIR,
            model=m,
        )
    if provider == "openai":
        return OpenAIClient(model=m)
    if provider == "deepseek":
        return DeepseekClient(model=m)
    if provider == "mistral":
        return MistralClient(model=m)
    raise ValueError(f"Unknown provider: {provider}")


def make_all_default_clients(**kwargs) -> dict[Provider, LLMClient]:
    """Construct one client per provider with the default-pinned model."""
    return {p: make_client(p, **kwargs) for p in DEFAULT_MODELS}


__all__ = [
    "LLMClient",
    "LLMResponse",
    "Provider",
    "DEFAULT_MODELS",
    "ANTHROPIC_CACHE_DIR",
    "make_client",
    "make_all_default_clients",
    "hash_text",
]
