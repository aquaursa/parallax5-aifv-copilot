# Contributing to PARALLAX-5 AI-FV Co-Pilot

Thanks for your interest. This is a research-software project.

## Scope

The co-pilot accepts contributions in three categories:

1. **Prompt and pipeline improvements.** Better prompts, better post-
   processing of LLM output, better extraction of Lean code from
   conversational responses. PRs should include before/after acceptance-
   rate measurements on at least 10 corpus contracts.
2. **LLM provider adapters.** New providers welcome. Adapters must
   implement the `LLMClient` protocol in `src/parallax5_aifv_copilot/llm/base.py`,
   support pinned model identifiers, and respect rate limits.
3. **Corpus contributions.** New contracts must come with provenance
   (Etherscan link or original repository), a stated obligation set
   from the PARALLAX-5 vocabulary (A1–A5), and a difficulty estimate.

## Non-acceptance bar

A contribution that decreases overall acceptance rate without
documenting *why* will not be accepted. Empirical regressions are real;
honest negative results are welcome but must be labeled as such.

## What we will not do

- Add prompts that bias the kernel toward acceptance. The kernel must
  decide on the merits of each draft.
- Add post-processing that fixes broken LLM proofs (e.g. inserting
  missing `by` keywords). The acceptance rate must reflect what LLMs
  actually produce.
- Add result-massaging that excludes "hard" contracts from headline
  numbers. The full corpus is the corpus.

## Reporting issues

Use the GitHub issue tracker. For security issues, see `SECURITY.md`.

## Code style

- Python: ruff + mypy strict; line length 110.
- Lean: project-wide style follows the substrate (`parallax-5/lean/`).
- Markdown: 80-col soft wrap, headings sentence case.
