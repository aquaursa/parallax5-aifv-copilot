# Changelog

All notable changes to the PARALLAX-5 AI-FV Co-Pilot are documented in
this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial repository scaffold and project metadata.
- LLM provider adapters for Claude, OpenAI, Deepseek, and Mistral.
- Lean server interface for kernel-verified acceptance gating.
- Spec pipeline (Solidity → Lean 4 obligation-typed properties).
- Proof pipeline (statements → kernel-verified proofs).
- Benchmark harness for the 100-contract corpus.

### Planned for v0.1.0

- Complete 100-contract corpus with provenance manifest.
- First full benchmark run across all four LLM providers.
- Honest acceptance-rate report including failure-mode taxonomy.
- Docker image for reproducible execution.
- Zenodo deposit with its own DOI.
