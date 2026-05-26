"""Anthropic self-host adapter.

This adapter is for the case where the benchmark operator IS Claude
(no separate Anthropic API key needed). It reads pre-generated responses
from a deterministic on-disk cache keyed by SHA-256 of the prompt.

The cache is populated by the operator (Claude) generating responses
to the same prompts the harness will issue, then writing them to
`results/anthropic_cache/<cache_key>.json`. When the harness later
calls `.complete()`, the adapter computes the same cache key and reads
the pre-generated response — no network call, no separate API key.

This is intentionally NOT a transparent substitute for a real API
call: the report MUST disclose that the Anthropic responses were
produced interactively rather than through stored API credentials.
The disclosure is the honesty.
"""
from __future__ import annotations

import json
from pathlib import Path

from .base import LLMResponse, hash_text


class ClaudeSelfHostClient:
    """Cache-backed Anthropic adapter.

    The cache is a directory containing one JSON file per response:
        results/anthropic_cache/{cache_key}.json
    where cache_key = sha256(system_prompt + "\\n\\n" + user_prompt) hex.

    Each file is shape:
        {
          "prompt_id":       "spec-v1",
          "system_prompt":   "...",
          "user_prompt":     "...",
          "response_text":   "...",
          "produced_at":     "2026-05-26T...",
          "note":            "..."
        }
    """

    def __init__(
        self,
        cache_dir: Path,
        model: str = "claude-opus-4-7",
    ) -> None:
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = model

    @property
    def provider(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    def cache_path(self, system_prompt: str, user_prompt: str) -> Path:
        key = hash_text(system_prompt + "\n\n" + user_prompt)
        return self._cache_dir / f"{key}.json"

    def cache_key(self, system_prompt: str, user_prompt: str) -> str:
        return hash_text(system_prompt + "\n\n" + user_prompt)

    def has_cached(self, system_prompt: str, user_prompt: str) -> bool:
        return self.cache_path(system_prompt, user_prompt).exists()

    def store(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_text: str,
        prompt_id: str,
        note: str = "",
    ) -> Path:
        """Write a response to the cache. Used by the operator to prime
        the cache before benchmark runs."""
        p = self.cache_path(system_prompt, user_prompt)
        p.write_text(
            json.dumps(
                {
                    "prompt_id":     prompt_id,
                    "system_prompt": system_prompt,
                    "user_prompt":   user_prompt,
                    "response_text": response_text,
                    "model":         self._model,
                    "note":          note,
                },
                indent=2,
            )
        )
        return p

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        prompt_id: str,
        max_tokens: int = 8192,
        temperature: float = 0.0,
    ) -> LLMResponse:
        path = self.cache_path(system_prompt, user_prompt)
        if not path.exists():
            raise RuntimeError(
                f"Claude self-host: no cached response for prompt {hash_text(system_prompt + chr(10) + chr(10) + user_prompt)[:16]} "
                f"({prompt_id}). Prime the cache via .store() before running the benchmark."
            )
        cached = json.loads(path.read_text())
        text = cached["response_text"]
        # Approximate token counts (4 chars/token is the standard rough estimate).
        return LLMResponse(
            provider="anthropic",
            model=self._model,
            prompt_id=prompt_id,
            prompt_sha256=hash_text(system_prompt + "\n\n" + user_prompt),
            request_payload_sha256=hash_text(system_prompt + user_prompt),
            response_text=text,
            input_tokens=(len(system_prompt) + len(user_prompt)) // 4,
            output_tokens=len(text) // 4,
            duration_seconds=0.0,
            finish_reason="self_host_cache",
            raw_response_json={"source": "claude-self-host", "cache_path": str(path)},
        )
