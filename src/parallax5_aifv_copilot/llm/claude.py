"""Anthropic Claude adapter.

Default model: claude-opus-4-7 (pinned). Override via constructor for
benchmarks that want to compare across Claude versions.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMResponse, hash_text

_DEFAULT_MODEL = "claude-opus-4-7"


class ClaudeClient:
    """Anthropic API adapter."""

    def __init__(self, model: str = _DEFAULT_MODEL, api_key: str | None = None) -> None:
        from anthropic import Anthropic

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self._client = Anthropic(api_key=key)
        self._model = model

    @property
    def provider(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        prompt_id: str,
        max_tokens: int = 8192,
        temperature: float = 0.0,
    ) -> LLMResponse:
        payload = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        t0 = time.perf_counter()
        msg: Any = self._client.messages.create(**payload)
        elapsed = time.perf_counter() - t0

        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        return LLMResponse(
            provider="anthropic",
            model=self._model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(json.dumps(payload, sort_keys=True)),
            response_text=text,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
            duration_seconds=elapsed,
            finish_reason=msg.stop_reason or "unknown",
            raw_response_json=msg.model_dump() if hasattr(msg, "model_dump") else {},
        )
