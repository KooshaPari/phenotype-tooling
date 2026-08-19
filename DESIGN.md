# DESIGN.md — phenotype-tooling

## Overview

**phenotype-tooling** provides internal developer tooling for the phenotype ecosystem. It combines a Svelte frontend with Rust CLI crates and Node.js utilities for linting, auditing, code generation, and governance workflows across the polyrepo.

## Architecture

```
phenotype-tooling/
├── crates/                # Rust crates (CLI tools, linters, generators)
├── packages/              # Node.js / TypeScript shared packages
├── src/                   # Svelte frontend (governance dashboards)
├── scripts/               # Build and operational scripts
├── templates/             # Code generation templates
├── governance/            # Governance policy definitions
├── observability/         # Monitoring and tracing config
├── hooks/                 # Git hooks and CI triggers
├── tests/                 # Test suites
├── deploy/                # Deployment manifests
└── docs/                  # Internal documentation
```

## Key Design Decisions

1. **Rust + Svelte + TypeScript** — Rust for performance-critical linting, Svelte for UI, TS for glue
2. **Polyglot CLI** — unified command interface wrapping linters for Rust, TypeScript, Python, and Go
3. **Template-driven generation** — scaffold new repos and components from centralized templates
4. **Governance-as-code** — policies defined declaratively, enforced via pre-commit and CI

## Data Flow

```
Developer CLI → phenotype-tooling → Lint/Generate/Grade → Report → Governance Dashboard (Svelte)
```

## Non-Goals

- IDE extension distribution (VS Code extensions maintained separately)
- Runtime monitoring (handled by phenotype-infra observability)
- Public-facing documentation site (internal tooling only)

## Status

- Active development with absorption/review workflows
- Deprecation notices for superseded tools tracked in deprecation_notice.md
- SOTA.md tracks state-of-the-art tooling capabilities

## References

- [AGENTS.md](./AGENTS.md) — LLM contributor guidelines
- [SOTA.md](./SOTA.md) — Current capabilities snapshot
- [charter.md](./charter.md) — Team charter
