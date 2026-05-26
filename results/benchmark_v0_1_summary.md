# PARALLAX-5 AI-FV Co-Pilot — v0.1 Benchmark Report

> Run: `results/run_v0_1_1contract_4x4/`
> Date: 2026-05-26
> Corpus manifest: `corpus/manifest/v0.1-bench-1.json` (subset of `v0.1.json`)
> Substrate: `aquaursa/parallax-5` v1.0.1 (commit `e9ac9f27`,
>            [doi:10.5281/zenodo.20402755](https://doi.org/10.5281/zenodo.20402755))

## Headline number

**Of the 12 attempts where both the spec pipeline and the proof
pipeline produced valid Lean output, 12 were accepted by the Lean
kernel under the four-condition gate (`lake build` clean, theorem
signature preserved, no `sorry`/`admit`/`native_decide`, no new
`axiom`).**

| | Accepted | Total attempts |
|:-|:-:|:-:|
| Headline | **12** | **12** |
| Acceptance rate on attempts with valid drafts | **100%** | |

This is the result on **one** contract from the corpus:
`a1_trivial_constant_balance`, a minimal Solidity contract whose only
state is an `immutable` balance set at deployment.

## What this number does and does not mean

It means: the AI-FV Co-Pilot pipeline is operational end-to-end. Four
LLMs were independently prompted to draft Lean 4 specifications and
proofs of those specifications for a real Solidity contract; the Lean
kernel decided which drafts to accept under a deterministic
four-condition gate; the cross-validation matrix (every spec proven
by every prover) ran successfully.

It does **not** mean: that LLMs reliably solve smart-contract formal
verification. The contract chosen for v0.1 is the simplest in the
corpus — an immutable balance with no mutating operations. The A1
obligation reduces to `(deploy initial).balance = initial`, provable
by `rfl` after unfolding. On this contract, the LLMs were not asked
to do much. The v0.2 run on the full 100-contract corpus is the
substantive test.

## The cross-validation matrix

Three providers produced a valid Lean specification draft for this
contract:

| Spec provider | Model | Spec output (tokens) | Spec time |
|:-|:-|:-:|:-:|
| Anthropic | `claude-opus-4-7` (self-host, see below) | 304 | 0.0s |
| OpenAI | `gpt-5.5-pro` | 3752 | 107s |
| Deepseek | `deepseek-v4-pro` | 1424 | 32s |
| Mistral | `magistral-medium-2509` | (no Lean block extracted) | 112s |

The matrix of proof attempts and outcomes (rows = spec provider,
columns = proof provider):

| | proof:Anthropic | proof:OpenAI | proof:Deepseek | proof:Mistral |
|:-|:-:|:-:|:-:|:-:|
| **spec:Anthropic** | ✓ ACCEPT | ✓ ACCEPT | ✓ ACCEPT | ✓ ACCEPT |
| **spec:OpenAI** | ✓ ACCEPT | ✓ ACCEPT | ✓ ACCEPT | ✓ ACCEPT |
| **spec:Deepseek** | ✓ ACCEPT | ✓ ACCEPT | ✓ ACCEPT | ✓ ACCEPT |
| **spec:Mistral** | (no spec) | (no spec) | (no spec) | (no spec) |

Each cell ran with `temperature=0.0` against `prompts/spec_v1.md`
and `prompts/proof_v1.md`. Source files (verbatim Lean) are at
`results/run_v0_1_1contract_4x4/lean_files/`.

## Three honest disclosures

### 1. Anthropic responses were produced in an interactive session, not via API call

The Claude column was filled by the benchmark operator (also Claude
Opus 4.7) generating the responses interactively and storing them in
the deterministic cache at `results/anthropic_cache/<sha256>.json`.
The cache key is computed from `sha256(system_prompt + "\n\n" +
user_prompt)`, identical to what an API-routed `claude-opus-4-7` call
would receive. The cached responses are committed; another operator
running the benchmark with the same prompts will get bit-identical
behavior for the Anthropic column.

This is not a substitute for API-key-routed runs — the next operator
running the benchmark with *different* prompts will hit a cache miss
on the Anthropic column. For the v0.2 full-corpus run, the
self-hosted approach can be repeated to cover the additional 99
contracts, or an Anthropic API key can be provisioned to make the
Anthropic column auto-fill like the others.

### 2. Mistral spec extraction failed; the Mistral column ran on `magistral-medium-2509`, not `labs-leanstral-2603`

The roadmap-named `labs-leanstral-2603` model is on Mistral's Labs
tier, which requires admin enablement at
[admin.mistral.ai/plateforme/privacy](https://admin.mistral.ai/plateforme/privacy).
The benchmark operator has not yet completed this enablement step;
the adapter auto-falls back to `magistral-medium-2509`, a reasoning
model on Mistral's standard tier.

`magistral-medium-2509` produced a response for the spec prompt that
did not contain a parseable Lean code fence — the model's
typed-block output (`type: thinking` + `type: text`) extracted clean
text, but the text did not include the requested code fence. This is
a *pipeline-level* miss, not a *kernel* miss. The miss is reported
honestly here; no result is fabricated.

For proof drafting, by contrast, `magistral-medium-2509` produced
four valid proofs that the kernel accepted. This asymmetry is
interesting — the proof prompt is more constrained than the spec
prompt — and is worth investigating in v0.2.

### 3. A kernel-gate bug was found and fixed mid-run

The initial verification pass rejected all 12 attempts with the
reason "proposed theorem statement not present verbatim". The
`LeanServer.verify()` implementation was comparing the *full*
expected statement (which ends `:= by sorry` in the spec) against the
proof file (which has `:= by <real proof>`). This is over-strict and
produced a false-rejection cascade.

The fix (committed as part of this run) compares **theorem
signatures** — the substring from `theorem NAME ...` up to (but not
including) `:=`. This correctly accepts spec-vs-proof body
differences while still rejecting quiet weakening of the theorem
itself. A small test pair (`weakened theorem → rejected, identical
signature → accepted`) is included in `tests/test_infrastructure.py`.

## What the LLMs produced

Verbatim files for all 12 accepted proofs are at
`results/run_v0_1_1contract_4x4/lean_files/`. Brief samples below.

### Anthropic's spec (the simplest, 304 output tokens)

```lean
namespace Parallax5.Copilot.a1_trivial_constant_balance

structure ContractState where
  balance : Nat
  deriving Repr

def deploy (initial : Nat) : ContractState :=
  { balance := initial }

def obligationPredicate (s : ContractState) (initial : Nat) : Prop :=
  s.balance = initial

theorem a1_trivial_constant_balance_safety :
    ∀ (initial : Nat), obligationPredicate (deploy initial) initial := by
  sorry

end Parallax5.Copilot.a1_trivial_constant_balance
```

### Anthropic's own proof of its own spec

```lean
theorem a1_trivial_constant_balance_safety :
    ∀ (initial : Nat), obligationPredicate (deploy initial) initial := by
  intro initial
  unfold obligationPredicate
  unfold deploy
  rfl
```

### Deepseek's proof of OpenAI's spec (cross-validation)

OpenAI's spec used a different state structure (`ConstantBalanceState`
with an extra `initialBalance` field) and a different theorem shape
(`A1 s → A1 (getBalance s)`). Deepseek proved it anyway:

```lean
theorem a1_trivial_constant_balance_safety :
    ∀ (s : ConstantBalanceState),
      valueConservationA1 s → valueConservationA1 (getBalance s) := by
  intro s h
  unfold getBalance
  exact h
```

The pattern is "proving an invariance theorem under a no-op
operation" — true for all four provers across all three specs.
That every (spec, prover) pair could see a different state shape and
still produce an accepted proof is the cross-validation result this
benchmark is designed to surface.

## Timing breakdown

| Phase | Wall-clock |
|:-|:-:|
| Spec drafting (4 providers, parallel) | 113s |
| Proof drafting (3 specs × 4 provers, parallel) | 43s |
| Kernel verification (12 attempts, sequential) | 38s |
| **Total** | **~3.5 min** |

The Anthropic self-host returned in 0s (cache lookup); the
non-Anthropic providers ranged from 8s (Deepseek on a simple proof)
to 107s (OpenAI gpt-5.5-pro spec, which is reasoning-heavy and slow).

## Reproducing this run

```bash
git clone --recursive https://github.com/aquaursa/parallax5-aifv-copilot.git
cd parallax5-aifv-copilot
export OPENAI_API_KEY=... DEEPSEEK_API_KEY=... MISTRAL_API_KEY=...
# ANTHROPIC_API_KEY optional — if absent, Anthropic column reads from
# results/anthropic_cache/ which is committed in this repo.
docker build -t parallax5-aifv-copilot .
docker run --rm \
    -e OPENAI_API_KEY -e DEEPSEEK_API_KEY -e MISTRAL_API_KEY \
    parallax5-aifv-copilot \
    parallax5-aifv benchmark --corpus corpus/manifest/v0.1-bench-1.json
```

LLM outputs are temperature-zero but not bit-deterministic; the
*distribution* should reproduce, not the exact text.

## What comes next: v0.2

- Run the full 100-contract corpus (`corpus/manifest/v0.1.json`).
- Resolve the Mistral Labs enablement so the Leanstral model
  participates in the matrix.
- Investigate the Mistral spec-extraction failure pattern (likely a
  prompt-side fix or a typed-block-aware extractor).
- Provision an Anthropic API key OR populate the self-host cache for
  all 99 additional contracts.
- Compare obligation-class acceptance rates (does A4 fail more than
  A1?).
- Publish the run as a versioned Zenodo deposit alongside the
  substrate's `doi:10.5281/zenodo.20402755`.

The v0.1 contribution is the architecture: the four-condition gate,
the persistent `lean --server` session, the cache-backed self-host
pattern, and the cross-validation matrix all work. The v0.2
contribution will be the empirical result on the full corpus.
