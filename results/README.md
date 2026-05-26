# Benchmark results

Per-run outputs are written to subdirectories of this folder by
`parallax5-aifv benchmark`. The structure is:

```
results/
├── run_<UTC_TIMESTAMP>/
│   ├── attempts/             One JSON file per (contract, spec-LLM, proof-LLM)
│   ├── lean_files/           The .lean files submitted to the kernel
│   └── summary.json          Aggregate stats: total / accepted / by-pair
└── benchmark_v0.1_summary.md  The honest acceptance-rate report (committed)
```

Per-run `attempts/` and `lean_files/` directories are gitignored. The
aggregate `summary.json` files MAY be committed alongside the published
report when they're worth pinning.

Bulk run data lives at the corresponding Zenodo deposit (DOI assigned
after first full run); the GitHub repo carries only the summary
artifacts and the small subset of cases discussed in the report.
