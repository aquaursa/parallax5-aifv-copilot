"""OpenAI adapter.

Default model: gpt-5.5-pro (pinned).
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMResponse, hash_text

_DEFAULT_MODEL = "gpt-5.5-pro"


class OpenAIClient:
    """OpenAI Chat Completions adapter."""

    def __init__(self, model: str = _DEFAULT_MODEL, api_key: str | None = None) -> None:
        from openai import OpenAI

        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._client = OpenAI(api_key=key)
        self._model = model

    @property
    def provider(self) -> str:
        return "openai"

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
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_completion_tokens": max_tokens,
        }
        # GPT-5+ reasoning models don't take temperature
        if not self._model.startswith(("gpt-5", "o3", "o4")):
            payload["temperature"] = temperature

        t0 = time.perf_counter()
        resp = self._client.chat.completions.create(**payload)
        elapsed = time.perf_counter() - t0

        choice = resp.choices[0]
        return LLMResponse(
            provider="openai",
            model=self._model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(json.dumps(payload, sort_keys=True)),
            response_text=choice.message.content or "",
            input_tokens=resp.usage.prompt_tokens if resp.usage else 0,
            output_tokens=resp.usage.completion_tokens if resp.usage else 0,
            duration_seconds=elapsed,
            finish_reason=choice.finish_reason or "unknown",
            raw_response_json=resp.model_dump() if hasattr(resp, "model_dump") else {},
        )
