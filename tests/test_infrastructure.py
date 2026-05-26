"""Infrastructure tests that don't require LLM API keys or Lean.

These run in CI on every push. They check the scaffold's structural
contracts: prompts parse correctly, the corpus manifest schema validates,
LLM-response extraction works on canned inputs, etc.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from parallax5_aifv_copilot.pipelines import extract_lean_block
from parallax5_aifv_copilot.pipelines.spec import _split_prompt_file

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"


def test_spec_prompt_parses() -> None:
    """spec_v1.md must contain both a system and user prompt section."""
    sys_p, usr_p = _split_prompt_file(PROMPTS / "spec_v1.md")
    assert len(sys_p) > 100
    assert len(usr_p) > 50
    assert "PARALLAX-5" in sys_p
    assert "A1" in sys_p and "A5" in sys_p


def test_proof_prompt_parses() -> None:
    """proof_v1.md must contain both a system and user prompt section."""
    sys_p, usr_p = _split_prompt_file(PROMPTS / "proof_v1.md")
    assert len(sys_p) > 100
    assert len(usr_p) > 50
    # Forbidden tokens are documented in the user prompt's rules section
    full = sys_p + "\n" + usr_p
    assert "sorry" in full.lower()
    assert "axiom" in full.lower()


def test_extract_lean_block_handles_clean_response() -> None:
    response = """Here is the proof:

```lean
theorem foo : 1 + 1 = 2 := rfl
```

Done."""
    block = extract_lean_block(response)
    assert block is not None
    assert "theorem foo" in block


def test_extract_lean_block_handles_lean4_tag() -> None:
    response = """```lean4
theorem bar : True := trivial
```"""
    block = extract_lean_block(response)
    assert block is not None
    assert "trivial" in block


def test_extract_lean_block_returns_none_on_no_fence() -> None:
    assert extract_lean_block("just prose, no code fence") is None


def test_extract_lean_block_takes_first_fence() -> None:
    response = """```lean
theorem first : True := trivial
```

And then:

```lean
theorem second : True := trivial
```"""
    block = extract_lean_block(response)
    assert block is not None
    assert "first" in block
    assert "second" not in block


def test_llm_default_models_pinned() -> None:
    """Every default model must be a pinned identifier (no 'latest' aliases)."""
    from parallax5_aifv_copilot.llm import DEFAULT_MODELS
    assert set(DEFAULT_MODELS.keys()) == {"anthropic", "openai", "deepseek", "mistral"}
    for provider, model in DEFAULT_MODELS.items():
        assert "latest" not in model.lower(), (
            f"{provider} default model '{model}' uses 'latest' alias; "
            f"reproducibility requires a pinned identifier"
        )


def test_acceptance_verdict_structure() -> None:
    """AcceptanceVerdict captures all four kernel-gate conditions."""
    from parallax5_aifv_copilot.kernel import AcceptanceVerdict
    v = AcceptanceVerdict(
        accepted=False,
        file_path="/tmp/x.lean",
        statement_present=True,
        no_sorry=True,
        no_admit=True,
        no_axiom_intro=False,
        diagnostic_errors=[],
        diagnostic_warnings=[],
        elapsed_seconds=1.0,
        rejection_reason="introduced axiom",
    )
    # All four conditions are reachable on the dataclass surface.
    assert hasattr(v, "statement_present")
    assert hasattr(v, "no_sorry")
    assert hasattr(v, "no_admit")
    assert hasattr(v, "no_axiom_intro")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
