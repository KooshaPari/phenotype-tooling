# SOTA — phenotype-tooling

> **Last researched:** 2026-06-16  
> **Methods:** FocalPoint lift audit, scripting policy review, absorption execution plans, internal dogfood

## Executive summary

| Dimension | Our choice | Confidence | Deep dive |
|-----------|------------|------------|-----------|
| Technical | Rust workspace + absorbed multi-stack subdirs | high | [docs/sota/technical.md](docs/sota/technical.md) |
| DX | `cargo install --path` + adopt-tooling.sh shims | high | [docs/sota/dx.md](docs/sota/dx.md) |
| UX | N/A (developer tooling) | n/a | [docs/sota/ux.md](docs/sota/ux.md) |
| AX | Genesis doc set + federation workflows | high | [docs/sota/ax.md](docs/sota/ax.md) |
| Security | cargo-deny + trufflehog federation | high | [docs/sota/security.md](docs/sota/security.md) |
| Ops | Workspace CI + per-subdir smoke for absorbed tools | med | [docs/sota/ops.md](docs/sota/ops.md) |
| Cost | One tooling hub vs 30+ duplicated scripts | high | [docs/sota/cost.md](docs/sota/cost.md) |

## Why this is optimal (for our constraints)

Rust-first CLIs match the org scripting policy while a single workspace eliminates duplicated `quality-gate.sh` and traceability scripts. Absorbed repos keep independent build systems to avoid forcing TS/Python/Rust into one toolchain — federation at the workflow layer, not codegen monolith.

## Fork status

- **Is fork:** no

## Evolution triggers

Re-open research when:

- Consumer repo count exceeds federation maintainability
- Just/Bun CLI policy changes org-wide scripting hierarchy
- Major absorbed tool needs extraction back to standalone repo

## Linkage

- Charter scope: [charter.md](charter.md)
- Review enforcement: [review.md](review.md)
- Intent goals: [intent.md](intent.md)
