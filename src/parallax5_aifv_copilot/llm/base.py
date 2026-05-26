"""Base LLM client protocol.

Every provider adapter implements LLMClient. Adapters are responsible
for handling provider-specific authentication, retry logic, and
response parsing — but they all expose the same flat surface so the
pipelines can swap providers freely.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Verbatim record of one LLM call, suitable for committing as evidence."""

    provider: str
    model: str
    prompt_id: str
    prompt_sha256: str
    request_payload_sha256: str
    response_text: str
    input_tokens: int
    output_tokens: int
    duration_seconds: float
    finish_reason: str
    raw_response_json: dict[str, object] = field(default_factory=dict)


class LLMClient(Protocol):
    """Provider-agnostic interface for a single round-trip call."""

    @property
    def provider(self) -> str:
        ...

    @property
    def model(self) -> str:
        ...

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        prompt_id: str,
        max_tokens: int = 8192,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """One synchronous completion. Implementations must retry transient
        failures (rate limits, 5xx) but propagate hard failures."""
        ...


def hash_text(text: str) -> str:
    """SHA-256 of a UTF-8-encoded string, hex. Used for prompt fingerprints."""
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
