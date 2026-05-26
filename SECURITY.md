# Security Policy

## Reporting a vulnerability

Email `security@aquaursa.io` with details. Do not open a public issue
for security-relevant findings until they have been triaged.

For each report, include:

- the affected component (prompt, parser, kernel adapter, benchmark
  harness, Docker image, etc.),
- the conditions under which the issue manifests,
- a minimal reproduction.

## In scope

- **Kernel-gate bypass**: any sequence of inputs that causes a draft to
  be marked accepted without genuine kernel acceptance (no `sorry`,
  no `admit`, no `axiom` introduction, statement preserved exactly).
- **Provenance forgery**: tampering with corpus manifests or per-run
  metadata such that a result appears to come from an LLM/run that
  did not produce it.
- **Credential exfiltration**: any path by which API keys leave the
  environment they are configured in.
- **Reproducibility regressions**: changes that silently break the
  ability to reproduce documented acceptance rates.

## Out of scope

- The fact that LLM outputs are not byte-deterministic. This is
  acknowledged and documented; reproducibility is by distribution,
  not by identity.
- Provider-side outages or rate-limit behavior.
- Differences in acceptance rate across runs that fall within the
  documented sampling variance.
