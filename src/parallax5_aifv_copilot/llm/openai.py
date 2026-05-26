"""OpenAI adapter.

Default model: gpt-5.5-pro (pinned). gpt-5.5-pro is a reasoning model
that requires the Responses API (/v1/responses), not chat completions.

The adapter auto-routes: any model name containing 'pro' or matching
the reasoning model prefixes (o3, o4, gpt-5.X-pro) uses Responses;
everything else uses Chat Completions.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMResponse, hash_text

_DEFAULT_MODEL = "gpt-5.5-pro"
_BASE_URL = "https://api.openai.com/v1"


def _needs_responses_api(model: str) -> bool:
    """Pro / reasoning models live on /v1/responses; chat models on /v1/chat/completions."""
    m = model.lower()
    return (
        "-pro" in m
        or m.startswith("o3")
        or m.startswith("o4")
        or "-reasoning" in m
    )


class OpenAIClient:
    """OpenAI adapter with dual-endpoint routing."""

    def __init__(self, model: str = _DEFAULT_MODEL, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._key = key
        self._model = model
        self._http = httpx.Client(
            base_url=_BASE_URL,
            timeout=httpx.Timeout(300.0),
            headers={"Authorization": f"Bearer {self._key}"},
        )

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
        if _needs_responses_api(self._model):
            return self._complete_via_responses(system_prompt, user_prompt, prompt_id, max_tokens)
        return self._complete_via_chat(system_prompt, user_prompt, prompt_id, max_tokens, temperature)

    def _complete_via_responses(
        self, system_prompt: str, user_prompt: str, prompt_id: str, max_tokens: int
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self._model,
            "instructions": system_prompt,
            "input": user_prompt,
            "max_output_tokens": max_tokens,
        }
        t0 = time.perf_counter()
        r = self._http.post("/responses", json=payload)
        r.raise_for_status()
        elapsed = time.perf_counter() - t0
        body = r.json()

        text_parts: list[str] = []
        for block in body.get("output", []):
            if block.get("type") == "message":
                for content in block.get("content", []):
                    if content.get("type") in ("output_text", "text"):
                        text_parts.append(content.get("text", ""))

        usage = body.get("usage", {})
        return LLMResponse(
            provider="openai",
            model=self._model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(json.dumps(payload, sort_keys=True)),
            response_text="\n".join(text_parts),
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            duration_seconds=elapsed,
            finish_reason=body.get("status", "unknown"),
            raw_response_json=body,
        )

    def _complete_via_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        prompt_id: str,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_completion_tokens": max_tokens,
        }
        if not self._model.startswith("gpt-5"):
            payload["temperature"] = temperature

        t0 = time.perf_counter()
        r = self._http.post("/chat/completions", json=payload)
        r.raise_for_status()
        elapsed = time.perf_counter() - t0
        body = r.json()

        choice = body["choices"][0]
        usage = body.get("usage", {})
        return LLMResponse(
            provider="openai",
            model=self._model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(json.dumps(payload, sort_keys=True)),
            response_text=choice["message"].get("content") or "",
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            duration_seconds=elapsed,
            finish_reason=choice.get("finish_reason", "unknown"),
            raw_response_json=body,
        )
