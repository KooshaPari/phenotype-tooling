# CANONICAL_REDIRECT — `phenotype-config` → `Configra`

**Date:** 2026-06-17
**ADR:** [ADR-031](https://github.com/KooshaPari/repos/blob/main/docs/adr/2026-06-17/ADR-031-configra-absorb.md)
**Status:** EFFECTIVE (28-day archive grace: 2026-07-15)

---

This file is a **canonical redirect marker**. Any tooling, CI, or consumer
that previously pointed at this repository (`KooshaPari/phenotype-config`)
**MUST** now point at the canonical replacement.

## Canonical replacement

| Concern | Old repo | New canonical repo |
|---|---|---|
| Rust config (canonical) | `KooshaPari/phenotype-config` | [`KooshaPari/Configra`](https://github.com/KooshaPari/Configra) |
| Rust config (this crate, `settly/`) | `KooshaPari/phenotype-config` (was: `crates/settly/`) | [`KooshaPari/Configra:feat/settly-crate-absorption`](https://github.com/KooshaPari/Configra/pull/44) (will be: `crates/settly/`) |
| TS edge bindings | `KooshaPari/Conft` | `KooshaPari/Conft` (unaffected per ADR-022) |

## Consumers that must update

| Consumer | Was | Now |
|---|---|---|
| `phenotype-mcp-router` Cargo.toml dep | `phenotype-config = { git = "phenotype-config" }` | `configra = { git = "Configra" }` (after PR #44 merges) |
| `pheno-registry` workspace member | `crates/phenotype-config` | `crates/configra` (after PR #44 merges) |
| CI templates (`pheno-ci-templates`) | `phenotype-config`-specific paths | `Configra`-specific paths |
| `pheno-context` adapter | ports referenced `phenotype-config::*` | ports reference `configra::*` (after PR #44 merges) |

## Per-ADR-022 two-crate split (still in force)

ADR-022's Rust/TS edge split is **preserved**:

- **Rust edge** = `Configra` (was: `phenotype-config`)
- **TS edge** = `Conft` (unaffected)

ADR-031 only changes the **name** of the Rust canonical repo, not the split.

## Timeline

- **2026-06-17**: This file authored; ADR-031 effective
- **2026-06-17**: Configra PR #44 opened (settly absorb)
- **2026-07-15**: `phenotype-config` archive (28-day grace period)
- **After 2026-07-15**: This repo becomes read-only; redirects enforced via GitHub's redirect mechanism

L5-104.7 — T19.4 (phenotype-config canonical redirect)
