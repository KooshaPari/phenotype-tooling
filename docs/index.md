# Phenotype Tooling

Phenotype Tooling is the shared Rust workspace for developer automation across
the Phenotype repo set. It centralizes quality gates, documentation checks,
release utilities, traceability scanners, and agent-operation helpers that were
previously duplicated across projects.

## What It Provides

| Area | Tools |
| --- | --- |
| Quality | `quality-gate`, `docs-health`, `doc-link-check` |
| Traceability | `fr-trace`, `fr-coverage`, `temporal-grounding` |
| Release | `release-cut`, `commit-msg-check`, `sbom-gen` |
| Governance | `legacy-scan`, `audit-privacy`, `bench-guard` |
| Agent Ops | `agent-orchestrator`, `agent-forecast`, `anthropic-usage-poll` |

## Quick Start

```bash
cargo check --workspace
cargo test --workspace
cargo install --path crates/quality-gate
```

Use the [tool catalog](./tools.md) to find the right binary and the
[adoption guide](./adoption.md) to wire it into another Phenotype repo.
