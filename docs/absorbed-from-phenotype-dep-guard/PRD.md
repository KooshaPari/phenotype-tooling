# PRD — phenotype-dep-guard

## Overview

`phenotype-dep-guard` is a supply-chain security tool for the Phenotype ecosystem. It performs multi-source dependency resolution, heuristic triage, AST-level static analysis, and malicious-code detection across direct and transitive dependencies.

## Goals

- Prevent malicious or compromised packages from entering the build graph.
- Surface vulnerability, license, and anomaly findings pre-merge and in CI.
- Integrate into the Phenotype governance layer as an enforceable policy gate.

## Epics

### E1 — Dependency Resolution
- E1.1 Resolve direct and transitive deps from lock files (pip, npm, cargo, go.mod).
- E1.2 Cross-reference resolved packages against OSV, NVD, and custom rule sets.
- E1.3 Cache resolution results with TTL for fast repeat runs.

### E2 — Static Triage
- E2.1 AST-parse Python/JS package code for known malicious patterns.
- E2.2 Detect install-time scripts (`setup.py` hooks, `postinstall`) with I/O or network access.
- E2.3 Score each finding with a severity level (critical / high / medium / low / info).

### E3 — Policy Engine
- E3.1 Read policy rules from `contracts/reconcile.rules.yaml`.
- E3.2 Block or warn on policy violations at the CLI exit code level.
- E3.3 Produce structured JSON/SARIF report artifacts.

### E4 — CI Integration
- E4.1 Provide a GitHub Actions workflow step that runs dep-guard on PRs.
- E4.2 Post findings as PR annotations via the GitHub Checks API.
- E4.3 Support `--fail-on=critical` threshold flag.

### E5 — Agent Integration
- E5.1 Expose a programmatic Python API for use by Phenotype agent pipelines.
- E5.2 Emit structured events consumable by helix-tracing / observability stack.

## Acceptance Criteria

- A clean repo with no known malicious deps produces exit code 0.
- A repo with a known-malicious package produces exit code 1 and a SARIF report.
- Policy violations matching `reconcile.rules.yaml` produce a blocking error message.
- All findings include package name, version, severity, and remediation hint.