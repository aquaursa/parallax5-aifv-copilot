# Changelog

All notable changes to the PARALLAX-5 AI-FV Co-Pilot are documented in
this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-05-26

### Added

- Full architecture: four-provider LLM adapters, spec/proof pipelines, persistent
  `lean --server` LSP-based kernel-acceptance gate, benchmark harness, CLI.
- 100-contract corpus across five tiers (synthetic exemplars, substrate-shipped
  contracts, catalog incident reproductions, Etherscan-fetched production code,
  vulnerability exemplars) with provenance manifest at `corpus/manifest/v0.1.json`.
- ClaudeSelfHostClient: deterministic cache-backed Anthropic adapter for runs
  by an operator who is themselves Claude (no separate API key required).
- v0.1 benchmark run: `results/run_v0_1_1contract_4x4/` covers the contract
  `a1_trivial_constant_balance` across the full 3-provider × 4-provider matrix
  with 12/12 kernel-accepted proofs (`results/benchmark_v0_1_summary.md`).
- Persistent `lean --server` LSP session: ~4s per verification once the project
  is warm, vs. ~30s per fresh `lake build` per file.
- Docker image, GitHub Actions CI, infrastructure unit tests (all green).

### Fixed

- `LeanServer.verify()` `statement_present` check was comparing full statements
  (including `:= by sorry` body) against proof files (with `:= by <real proof>`)
  and producing a false-rejection cascade. Fixed to compare theorem signatures
  (the substring before `:=`). Quiet-weakening rejection preserved and tested.

### Documented gaps to address in v0.2

- Mistral `labs-leanstral-2603` (the roadmap-named Lean-finetuned model)
  requires Labs-tier admin enablement at the Mistral console. Adapter
  auto-falls back to `magistral-medium-2509` until enabled. v0.1 ran the
  Mistral column on the fallback model.
- Mistral spec extraction produced no Lean code fence on `a1_trivial_constant_balance`
  (proof extraction worked). Likely a prompt-side fix or a typed-block-aware
  extractor.
- 99 of the 100 corpus contracts have NOT been benchmarked yet. v0.2 ships the
  full-corpus run.
- Anthropic responses for the v0.1 run were produced in an interactive Claude
  session and cached. v0.2 either uses an API key or extends the cache.

## [Unreleased] (post-0.1.0)

(Reserved for next-version notes.)
