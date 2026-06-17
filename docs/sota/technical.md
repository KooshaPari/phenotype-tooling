# Technical — SOTA (phenotype-tooling)

## Use case

Deliver Rust-first developer tooling (quality gates, doc checks, release, SBOM) and host absorbed standalone tools under the `platform/tooling` domain role.

**AgilePlus / FR trace:** FocalPoint Section 6 lift; scripting policy compliance

## Requirements

| Requirement | Weight |
|-------------|--------|
| Rust default for new scripts/CLIs | must |
| Workspace members independently testable | must |
| Absorbed subdirs keep own build system | must |
| Reusable workflow federation for fleet | should |
| Genesis governance at repo root | must |

## Language placement

| Component | Lang | Tier | Rationale |
|-----------|------|------|-----------|
| quality-gate, docs-health, fr-trace, etc. | Rust | 1 | Scripting policy default; correctness-critical CI |
| byteport, heliosapp frontends | TS | 2 | Absorbed product UI; build in subdir |
| policystack federation | TS + Python | 2 | Absorbed upstream stack |
| nanovms | Rust (standalone) | 1 | VM isolation crate; not forced into workspace |
| Shell shims during migration | Bash | transitional | Thin wrappers only until decommission |

## Alternatives considered

| Alternative | Type | Pros | Cons | Verdict |
|-------------|------|------|------|---------|
| Per-repo shell quality-gate.sh | internal | familiar | 30+ duplicates; policy drift | rejected |
| Python-only tooling repo | internal | fast scripts | violates Rust-first policy | rejected |
| Force all absorbed tools into one Cargo workspace | internal | single CI | breaks TS/Python stacks | rejected |
| N standalone tool repos | internal | isolation | N× governance | rejected |
| **Rust workspace + absorbed subdirs + federation** | chosen | policy aligned; proportional CI | multi-stack maintenance | **chosen** |

Research sources: phenotype-infrakit scripting policy, FocalPoint PLAN.md, absorption execution docs.

## Chosen strategy

Primary surface is the Rust workspace (`cargo check/test/clippy --workspace`). Absorbed tools under `crates/` build from their subdirs. Fleet consumers adopt binaries via `cargo install --path` or `scripts/adopt-tooling.sh`. GitHub reusable workflows centralize cargo-deny and secret scan.

Link: [charter.md](../../../charter.md) · [intent.md](../../../intent.md)

## Evolution triggers

Re-open when:

- Scripting policy elevates Bun/TS for new CLIs
- Workspace exceeds ~40 members without feature grouping
- Federation workflow count causes GitHub org limits

Update [alternatives.md](alternatives.md) and [../../../SOTA.md](../../../SOTA.md) when verdict changes.
