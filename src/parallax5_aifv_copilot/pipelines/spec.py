"""Spec pipeline: Solidity → Lean 4 obligation-typed statement.

For each (contract, LLM) pair we:

  1. Load the versioned prompt template from prompts/.
  2. Construct a user message with the contract source.
  3. Call the LLM.
  4. Extract the Lean 4 code block from the response.
  5. Return both the statement and the verbatim LLM response (the
     latter is committed as evidence under results/).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ..llm import LLMClient, LLMResponse


@dataclass(frozen=True, slots=True)
class SpecDraft:
    contract_id: str
    provider: str
    model: str
    statement: str                 # extracted Lean 4 theorem (no proof body)
    full_response: LLMResponse     # verbatim provider output


_FENCE_RE = re.compile(
    r"```(?:lean4?)?\s*\n(.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)


def _split_prompt_file(prompt_path: Path) -> tuple[str, str]:
    """Parse `prompts/spec_v1.md`: returns (system_prompt, user_prompt)."""
    raw = prompt_path.read_text()
    # Look for `## System prompt` and `## User prompt` headers
    parts = re.split(r"\n##\s+(System prompt|User prompt)\s*\n", raw)
    if len(parts) < 5:
        raise ValueError(
            f"Prompt file {prompt_path} must contain '## System prompt' "
            f"and '## User prompt' sections"
        )
    # parts = [pre, 'System prompt', system_body, 'User prompt', user_body, ...]
    system = parts[2].strip()
    user = parts[4].strip()
    return system, user


def extract_lean_block(response_text: str) -> str | None:
    """Extract the first Lean code fence from a model response."""
    m = _FENCE_RE.search(response_text)
    if not m:
        return None
    return m.group(1).strip()


def draft_spec(
    *,
    client: LLMClient,
    contract_id: str,
    contract_source: str,
    contract_purpose: str,
    prompt_path: Path,
) -> SpecDraft | None:
    """Run the spec pipeline against one (contract, LLM) pair.

    Returns None if the model produced no extractable Lean block. The
    caller is responsible for logging the verbatim response in either case.
    """
    system_prompt, user_template = _split_prompt_file(prompt_path)
    user_prompt = (
        f"{user_template}\n\n"
        f"---\n"
        f"**Contract name:** {contract_id}\n"
        f"**Purpose:** {contract_purpose}\n\n"
        f"```solidity\n{contract_source}\n```\n"
    )

    response = client.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        prompt_id="spec-v1",
        max_tokens=4096,
        temperature=0.0,
    )

    statement = extract_lean_block(response.response_text)
    if statement is None:
        return None
    return SpecDraft(
        contract_id=contract_id,
        provider=client.provider,
        model=client.model,
        statement=statement,
        full_response=response,
    )
