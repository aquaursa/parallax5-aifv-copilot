"""Deepseek adapter.

Default model: deepseek-v4-pro (pinned). Deepseek uses an OpenAI-
compatible chat-completions endpoint.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMResponse, hash_text

_DEFAULT_MODEL = "deepseek-v4-pro"
_BASE_URL = "https://api.deepseek.com/v1"


class DeepseekClient:
    """Deepseek API adapter."""

    def __init__(self, model: str = _DEFAULT_MODEL, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")
        self._key = key
        self._model = model
        self._http = httpx.Client(
            base_url=_BASE_URL,
            timeout=httpx.Timeout(180.0),
            headers={"Authorization": f"Bearer {self._key}"},
        )

    @property
    def provider(self) -> str:
        return "deepseek"

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
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        t0 = time.perf_counter()
        r = self._http.post("/chat/completions", json=payload)
        r.raise_for_status()
        elapsed = time.perf_counter() - t0
        body = r.json()

        choice = body["choices"][0]
        usage = body.get("usage", {})
        return LLMResponse(
            provider="deepseek",
            model=self._model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(json.dumps(payload, sort_keys=True)),
            response_text=choice["message"]["content"] or "",
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            duration_seconds=elapsed,
            finish_reason=choice.get("finish_reason", "unknown"),
            raw_response_json=body,
        )
