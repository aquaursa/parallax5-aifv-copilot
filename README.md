# PARALLAX-5 AI-FV Co-Pilot

**LLM proposes; Lean disposes.**

An application-layer instance of the AI-assisted formal verification (AI-FV) pattern, specialized to the [PARALLAX-5 substrate](https://github.com/aquaursa/parallax-5). Four frontier LLMs draft obligation-typed properties from Solidity contracts and Lean 4 proofs of those properties; the Lean kernel is the sole authority that decides which drafts count.

<table>
  <tr><td><strong>Status</strong></td>      <td>v0.1 — public benchmark in progress</td></tr>
  <tr><td><strong>Substrate</strong></td>   <td><a href="https://github.com/aquaursa/parallax-5">PARALLAX-5 v1.0.1</a> · <a href="https://doi.org/10.5281/zenodo.20402755">doi:10.5281/zenodo.20402755</a></td></tr>
  <tr><td><strong>Corpus</strong></td>      <td>100 contracts (assembly in progress)</td></tr>
  <tr><td><strong>License</strong></td>     <td>Apache-2.0</td></tr>
</table>

## The framing

The co-pilot **does not create trust**. It accelerates two things humans currently do slowly:

1. **Property authoring** — translating "this contract should conserve value" into a Lean 4 statement that names the right state, the right transitions, and the right obligations from the PARALLAX-5 vocabulary.
2. **Proof drafting** — producing a candidate proof of that statement against the substrate's typeclass instances over `EvmYul.EVM.State`.

Both of those activities admit verification: a proposed property is either well-typed Lean or not; a proposed proof is either kernel-accepted with zero `sorry`/`admit`/`axiom`-introductions or it is not. The co-pilot's contribution is to do the human work of writing the candidate; the Lean 4 kernel does the work of deciding whether to believe it.

**Trust authority remains with the kernel.** A draft that the kernel rejects is a rejected draft, regardless of which LLM produced it, how confident the LLM appeared, or how many LLMs converged on similar text.

## Cross-LLM protocol

Four models propose drafts in parallel. Each draft is verified independently:

| Provider | Model |
|---|---|
| Anthropic | `claude-opus-4-7` |
| OpenAI | `gpt-5.5-pro` |
| Deepseek | `deepseek-v4-pro` |
| Mistral | `labs-leanstral-2603` |

For each (contract, obligation) pair we record: which models produced a draft, which drafts kernel-accepted, and the exact accepted proof terms. Inter-model agreement is *evidence about LLM behavior*, not a substitute for kernel acceptance.

## Acceptance gate

A draft is **kernel-accepted** iff all four conditions hold:

1. The file compiles with `lake build` returning exit code 0.
2. The proposed theorem is present with the proposed statement (no quiet weakening).
3. The proof body contains zero `sorry`, `admit`, or `axiom` introductions.
4. No new `axiom` declarations were added to the project.

Anything else is **rejected**, and the LLM's verbatim response plus the kernel's verbatim error message are logged to `results/rejections/`.

## Quickstart

```bash
git clone --recursive https://github.com/aquaursa/parallax5-aifv-copilot.git
cd parallax5-aifv-copilot
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... DEEPSEEK_API_KEY=... MISTRAL_API_KEY=...
docker build -t parallax5-aifv-copilot .
docker run --rm -it \
    -e ANTHROPIC_API_KEY -e OPENAI_API_KEY -e DEEPSEEK_API_KEY -e MISTRAL_API_KEY \
    parallax5-aifv-copilot \
    parallax5-aifv benchmark --corpus corpus/manifest/v0.1.json
```

The benchmark writes per-attempt logs to `results/` and emits a structured acceptance-rate report.

## Reproducibility

LLM outputs are not bit-deterministic. The benchmark is **re-runnable to produce comparable distributions**, not byte-identical re-runs. The pinned environment fixes:

- Provider-side: model IDs explicitly versioned (no `-latest` aliases except where the provider does not offer pinned IDs).
- Local-side: Lean 4 toolchain pinned in `lean-toolchain`; Python pinned in `pyproject.toml`; the substrate pinned by submodule SHA.
- Prompt-side: all prompts versioned under `prompts/` and stamped into each result.

Per-run sampling variance is logged. Multiple runs of the benchmark are encouraged; the headline number is *median acceptance rate over N≥3 runs*, not the result of any single run.

## Repository structure

```
parallax5-aifv-copilot/
├── corpus/                      The 100-contract benchmark corpus
│   ├── contracts/               Solidity sources (provenance in manifest)
│   └── manifest/                Per-version corpus manifests (v0.1.json, …)
├── prompts/                     Versioned prompt templates
├── src/parallax5_aifv_copilot/
│   ├── llm/                     Provider adapters (Claude, GPT, Deepseek, Mistral)
│   ├── pipelines/               Spec pipeline + proof pipeline
│   ├── kernel/                  Lean server interface (LSP via lean --server)
│   ├── benchmark/               Run harness
│   └── cli.py                   Entry point
├── lean-substrate/              Pinned PARALLAX-5 substrate (git submodule)
├── tests/
├── results/                     Per-run outputs (gitignored bulk; summary committed)
├── docs/                        Methodology, prompt rationale, failure-mode taxonomy
├── Dockerfile
├── pyproject.toml
├── lean-toolchain
└── README.md
```

## How this fits the PARALLAX-5 substrate

The substrate already mechanizes 95 theorems over an abstract state machine, with a refinement instance to EvmYulLean's Cancun-fork EVM. The co-pilot's job is to extend that mechanization to **per-contract** specifications: take an arbitrary Solidity contract, articulate which of the five obligations it must satisfy, draft proofs of those obligations against the substrate's typeclass instances, and ship the kernel-accepted ones.

This addresses the substrate's most honest limitation, surfaced in §24 of the paper: *the 95-theorem mechanization is at the abstract layer; per-deployment certification still requires hand-mechanized instances*. The co-pilot is the production-volume bridge.

## Citation

```bibtex
@software{parallax5_aifv_copilot_2026,
  author    = {{AquaUrsa Research}},
  title     = {{PARALLAX-5 AI-FV Co-Pilot: LLM-Drafted, Kernel-Verified
                Smart-Contract Proofs}},
  year      = {2026},
  url       = {https://github.com/aquaursa/parallax5-aifv-copilot},
  note      = {Companion to PARALLAX-5 substrate at doi:10.5281/zenodo.20402755}
}
```

## Acknowledgments

PARALLAX-5 substrate (AquaUrsa Research). EvmYulLean (Nethermind). Mathlib (Lean 4 community). The four frontier model providers whose APIs make the co-pilot possible.
