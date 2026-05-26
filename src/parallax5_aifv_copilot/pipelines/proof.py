"""Proof pipeline: (Solidity, statement) → Lean 4 proof.

For each (statement, LLM) pair we:

  1. Load the versioned proof prompt template.
  2. Construct a user message with the contract source AND the statement.
  3. Call the LLM.
  4. Extract the proof file content.
  5. Return both the proof and the verbatim LLM response.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..llm import LLMClient, LLMResponse
from .spec import _split_prompt_file, extract_lean_block


@dataclass(frozen=True, slots=True)
class ProofDraft:
    contract_id: str
    statement_provider: str           # which LLM produced the spec
    proof_provider: str               # which LLM produced this proof
    model: str
    lean_file_content: str            # full .lean file content (statement + proof)
    full_response: LLMResponse


def draft_proof(
    *,
    client: LLMClient,
    contract_id: str,
    contract_source: str,
    statement_provider: str,
    statement: str,
    prompt_path: Path,
) -> ProofDraft | None:
    """Run the proof pipeline against one (statement, LLM) pair."""
    system_prompt, user_template = _split_prompt_file(prompt_path)
    user_prompt = (
        f"{user_template}\n\n"
        f"---\n"
        f"**Contract:** {contract_id}\n\n"
        f"```solidity\n{contract_source}\n```\n\n"
        f"**Theorem statement to prove:**\n\n"
        f"```lean\n{statement}\n```\n"
    )

    response = client.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        prompt_id="proof-v1",
        max_tokens=8192,
        temperature=0.0,
    )

    proof = extract_lean_block(response.response_text)
    if proof is None:
        return None

    # Wrap in a complete Lean 4 file. The substrate is imported via
    # `import PARALLAX5` which the project's lakefile arranges.
    file_content = (
        "import PARALLAX5\n\n"
        "open PARALLAX5\n\n"
        f"{proof}\n"
    )
    return ProofDraft(
        contract_id=contract_id,
        statement_provider=statement_provider,
        proof_provider=client.provider,
        model=client.model,
        lean_file_content=file_content,
        full_response=response,
    )
