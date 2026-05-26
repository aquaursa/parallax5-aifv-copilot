"""Benchmark harness: iterate corpus × LLMs × kernel verification.

For a corpus of N contracts and M LLMs, the matrix is:

  N contracts × M spec-drafters × M proof-drafters × 1 kernel = N·M·M attempts

Each attempt produces an `AttemptRecord` written to results/run_<ts>/.
The headline acceptance rate is the fraction of attempts the Lean kernel
accepts under the four-condition gate.
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from ..kernel import AcceptanceVerdict, LeanServer
from ..llm import LLMClient, Provider
from ..pipelines import draft_proof, draft_spec


@dataclass(frozen=True, slots=True)
class CorpusEntry:
    contract_id: str
    source_path: str
    purpose: str
    expected_obligations: list[str]   # e.g. ["A1", "A4"]
    provenance: str                   # Etherscan URL or repo + commit SHA
    notes: str = ""


@dataclass
class AttemptRecord:
    """One full (contract, spec-LLM, proof-LLM) attempt."""

    contract_id: str
    expected_obligations: list[str]
    spec_provider: str
    spec_model: str
    spec_statement: str | None
    spec_response_text: str
    spec_response_tokens_in: int
    spec_response_tokens_out: int
    spec_duration_seconds: float
    proof_provider: str
    proof_model: str
    proof_file_content: str | None
    proof_response_text: str
    proof_response_tokens_in: int
    proof_response_tokens_out: int
    proof_duration_seconds: float
    verdict: AcceptanceVerdict | None
    timestamp_utc: str

    def accepted(self) -> bool:
        return self.verdict is not None and self.verdict.accepted


def load_corpus(manifest_path: Path) -> list[CorpusEntry]:
    """Load corpus manifest (corpus/manifest/v0.1.json) → entries."""
    raw = json.loads(manifest_path.read_text())
    return [CorpusEntry(**e) for e in raw["contracts"]]


def _run_one_attempt(
    *,
    entry: CorpusEntry,
    contract_source: str,
    spec_client: LLMClient,
    proof_client: LLMClient,
    spec_prompt: Path,
    proof_prompt: Path,
    work_dir: Path,
    lean_server: LeanServer,
) -> AttemptRecord:
    ts = datetime.now(UTC).isoformat()

    # Step 1: spec drafting
    spec = draft_spec(
        client=spec_client,
        contract_id=entry.contract_id,
        contract_source=contract_source,
        contract_purpose=entry.purpose,
        prompt_path=spec_prompt,
    )

    if spec is None:
        # Model produced no extractable Lean. Record and move on.
        return AttemptRecord(
            contract_id=entry.contract_id,
            expected_obligations=entry.expected_obligations,
            spec_provider=spec_client.provider,
            spec_model=spec_client.model,
            spec_statement=None,
            spec_response_text="",
            spec_response_tokens_in=0,
            spec_response_tokens_out=0,
            spec_duration_seconds=0.0,
            proof_provider=proof_client.provider,
            proof_model=proof_client.model,
            proof_file_content=None,
            proof_response_text="",
            proof_response_tokens_in=0,
            proof_response_tokens_out=0,
            proof_duration_seconds=0.0,
            verdict=None,
            timestamp_utc=ts,
        )

    # Step 2: proof drafting
    proof = draft_proof(
        client=proof_client,
        contract_id=entry.contract_id,
        contract_source=contract_source,
        statement_provider=spec_client.provider,
        statement=spec.statement,
        prompt_path=proof_prompt,
    )

    if proof is None:
        return AttemptRecord(
            contract_id=entry.contract_id,
            expected_obligations=entry.expected_obligations,
            spec_provider=spec_client.provider,
            spec_model=spec_client.model,
            spec_statement=spec.statement,
            spec_response_text=spec.full_response.response_text,
            spec_response_tokens_in=spec.full_response.input_tokens,
            spec_response_tokens_out=spec.full_response.output_tokens,
            spec_duration_seconds=spec.full_response.duration_seconds,
            proof_provider=proof_client.provider,
            proof_model=proof_client.model,
            proof_file_content=None,
            proof_response_text="",
            proof_response_tokens_in=0,
            proof_response_tokens_out=0,
            proof_duration_seconds=0.0,
            verdict=None,
            timestamp_utc=ts,
        )

    # Step 3: write the .lean file and submit to the kernel server
    lean_file = work_dir / f"Attempt_{entry.contract_id}_{spec_client.provider}_{proof_client.provider}.lean"
    lean_file.write_text(proof.lean_file_content)
    verdict = lean_server.verify(
        lean_file,
        expected_statement=spec.statement,
    )

    return AttemptRecord(
        contract_id=entry.contract_id,
        expected_obligations=entry.expected_obligations,
        spec_provider=spec_client.provider,
        spec_model=spec_client.model,
        spec_statement=spec.statement,
        spec_response_text=spec.full_response.response_text,
        spec_response_tokens_in=spec.full_response.input_tokens,
        spec_response_tokens_out=spec.full_response.output_tokens,
        spec_duration_seconds=spec.full_response.duration_seconds,
        proof_provider=proof_client.provider,
        proof_model=proof_client.model,
        proof_file_content=proof.lean_file_content,
        proof_response_text=proof.full_response.response_text,
        proof_response_tokens_in=proof.full_response.input_tokens,
        proof_response_tokens_out=proof.full_response.output_tokens,
        proof_duration_seconds=proof.full_response.duration_seconds,
        verdict=verdict,
        timestamp_utc=ts,
    )


def run_benchmark(
    *,
    corpus: Iterable[CorpusEntry],
    spec_clients: dict[Provider, LLMClient],
    proof_clients: dict[Provider, LLMClient],
    substrate_root: Path,
    prompts_dir: Path,
    output_dir: Path,
) -> Path:
    """Execute the full benchmark matrix and emit results.

    Returns the run directory containing per-attempt JSON records plus
    a `summary.json` aggregate.
    """
    run_id = datetime.now(UTC).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "attempts").mkdir(exist_ok=True)
    (run_dir / "lean_files").mkdir(exist_ok=True)

    spec_prompt = prompts_dir / "spec_v1.md"
    proof_prompt = prompts_dir / "proof_v1.md"

    records: list[AttemptRecord] = []
    with LeanServer(project_root=substrate_root) as srv:
        for entry in corpus:
            contract_source = Path(entry.source_path).read_text()
            for sp, sc in spec_clients.items():
                for pp, pc in proof_clients.items():
                    print(f"  • {entry.contract_id}  spec={sp}  proof={pp}", flush=True)
                    rec = _run_one_attempt(
                        entry=entry,
                        contract_source=contract_source,
                        spec_client=sc,
                        proof_client=pc,
                        spec_prompt=spec_prompt,
                        proof_prompt=proof_prompt,
                        work_dir=run_dir / "lean_files",
                        lean_server=srv,
                    )
                    records.append(rec)
                    # Persist immediately so a crashed run keeps partial results.
                    record_path = run_dir / "attempts" / (
                        f"{entry.contract_id}__{sp}__{pp}.json"
                    )
                    record_path.write_text(json.dumps(asdict(rec), indent=2, default=str))

    # Summary
    summary = _summarize(records)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return run_dir


def _summarize(records: list[AttemptRecord]) -> dict[str, object]:
    n = len(records)
    accepted = sum(1 for r in records if r.accepted())
    by_pair: dict[str, dict[str, int]] = {}
    for r in records:
        key = f"{r.spec_provider}__{r.proof_provider}"
        by_pair.setdefault(key, {"total": 0, "accepted": 0})
        by_pair[key]["total"] += 1
        if r.accepted():
            by_pair[key]["accepted"] += 1
    return {
        "total_attempts": n,
        "accepted": accepted,
        "acceptance_rate": (accepted / n) if n else 0.0,
        "by_provider_pair": by_pair,
        "generated_at": datetime.now(UTC).isoformat(),
    }
