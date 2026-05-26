"""Mistral adapter.

Preferred model: labs-leanstral-2603 (the roadmap's named Lean-finetuned
variant). Leanstral is on Mistral's Labs tier and requires admin
enablement at https://admin.mistral.ai/plateforme/privacy.

Fallback model when Leanstral is unavailable: magistral-medium-2509 (a
reasoning model on the standard tier). The adapter attempts the
configured model first; on 403 'labs_not_enabled' it automatically
falls back to MISTRAL_FALLBACK_MODEL if set, otherwise propagates.

Magistral models return content as a list of typed blocks
([{'type': 'thinking', ...}, {'type': 'text', ...}]); the adapter
extracts the 'text' block.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import LLMResponse, hash_text

_DEFAULT_MODEL = "labs-leanstral-2603"
_DEFAULT_FALLBACK = "magistral-medium-2509"
_BASE_URL = "https://api.mistral.ai/v1"


def _extract_text(content: Any) -> str:
    """Unify Mistral's two content shapes: plain string or typed-block list."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Magistral returns [{'type': 'thinking', ...}, {'type': 'text', 'text': '...'}]
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


class MistralClient:
    """Mistral adapter with auto-fallback from Leanstral to Magistral."""

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        api_key: str | None = None,
        fallback_model: str | None = None,
    ) -> None:
        key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not key:
            raise RuntimeError("MISTRAL_API_KEY not set")
        self._key = key
        self._model = model
        self._fallback = fallback_model or os.environ.get("MISTRAL_FALLBACK_MODEL", _DEFAULT_FALLBACK)
        self._using_fallback = False
        self._http = httpx.Client(
            base_url=_BASE_URL,
            timeout=httpx.Timeout(300.0),
            headers={"Authorization": f"Bearer {self._key}"},
        )

    @property
    def provider(self) -> str:
        return "mistral"

    @property
    def model(self) -> str:
        return self._fallback if self._using_fallback else self._model

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
        return self._call(system_prompt, user_prompt, prompt_id, max_tokens, temperature, self.model)

    def _call(
        self,
        system_prompt: str,
        user_prompt: str,
        prompt_id: str,
        max_tokens: int,
        temperature: float,
        model: str,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        t0 = time.perf_counter()
        r = self._http.post("/chat/completions", json=payload)

        # Auto-fallback on Labs unavailability
        if r.status_code == 403 and not self._using_fallback:
            try:
                err = r.json()
                if err.get("type") == "labs_not_enabled":
                    self._using_fallback = True
                    return self._call(
                        system_prompt, user_prompt, prompt_id, max_tokens, temperature, self._fallback
                    )
            except Exception:
                pass

        r.raise_for_status()
        elapsed = time.perf_counter() - t0
        body = r.json()

        choice = body["choices"][0]
        usage = body.get("usage", {})
        text = _extract_text(choice["message"].get("content"))

        return LLMResponse(
            provider="mistral",
            model=model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(json.dumps(payload, sort_keys=True)),
            response_text=text,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            duration_seconds=elapsed,
            finish_reason=choice.get("finish_reason", "unknown"),
            raw_response_json=body,
        )
