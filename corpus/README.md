# PARALLAX-5 AI-FV Benchmark Corpus

The corpus is a curated set of 100 Solidity contracts spanning the five
PARALLAX-5 obligations and the basis-observability axis from the
underlying substrate. The benchmark target is to measure, per LLM and
per (spec-LLM, proof-LLM) pair, what fraction of contracts admit a
kernel-accepted obligation-typed proof.

## Layout

```
corpus/
├── README.md            (this file)
├── manifest/
│   └── v0.1.json        Versioned corpus manifest
└── contracts/
    └── <contract_id>/
        ├── source.sol   Verbatim Solidity source
        ├── meta.json    Provenance + classification
        └── purpose.md   One-sentence purpose summary
```

## Manifest schema

`corpus/manifest/v<X>.json` lists each entry as:

```json
{
  "version": "0.1",
  "frozen_at": "2026-06-XX",
  "contracts": [
    {
      "contract_id": "cream_finance_first_depositor",
      "source_path": "corpus/contracts/cream_finance_first_depositor/source.sol",
      "purpose": "ERC-4626-style vault vulnerable to first-depositor inflation.",
      "expected_obligations": ["A1"],
      "provenance": "https://etherscan.io/address/0x...; commit b09b...",
      "notes": "Catalog incident G1. Vulnerable variant."
    },
    ...
  ]
}
```

The manifest is FROZEN at benchmark time. Any change to it produces a
new version (`v0.2.json`, etc.); benchmark runs cite the manifest
version they ran against.

## Curation sources (planned)

1. **Empirical catalog** (~53 entries). The PARALLAX-5 paper's
   53-incident catalog (paper §10) provides vulnerable + hardened
   variants for many archetypes; each pair contributes two entries.
2. **Top-TVL primary code** (~30 entries). Aave V3, Compound V3,
   Uniswap V3, MakerDAO, Lido — flagship contracts as positive
   baselines.
3. **Substrate demo contracts** (~10 entries). The three demos already
   in the substrate (vault, bridge, agent_gate) plus their hardened
   patches.
4. **Synthetic minimal examples** (~7 entries). One trivially-correct
   contract per obligation A1–A5, plus two trivially-violating ones.
   These calibrate the lower bound of the difficulty distribution.

Total target: 100. The manifest must be sourced + verified before the
first benchmark run; the scaffold here defines the schema and pipeline.

## Provenance

Every entry MUST carry a stable URL or commit-SHA reference. Sources
that vanish (deleted Etherscan-verified contracts, etc.) are flagged
in `meta.json`. The benchmark report explicitly documents whether each
source was reachable at run time.

## What the corpus is NOT

- It is not a vulnerability test set. The obligation predicates are
  precise; a contract may satisfy them while still being economically
  unwise.
- It is not a difficulty-balanced benchmark. The contracts are drawn
  from real-world deployment; the difficulty distribution is what it
  is, not a designed pyramid.
- It is not closed under safety. Adversarial future contracts may
  defeat the corpus; we revisit on a forward-test cadence (see paper
  §10.5 forward-test methodology).
