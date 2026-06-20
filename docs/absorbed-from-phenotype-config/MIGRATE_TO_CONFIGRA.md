# phenotype-config → Configra Migration Plan

**ADR-031 supersedes ADR-022 naming.**
**Date:** 2026-06-17
**Owner:** orchestrator (claude opus 4.7)
**Companion:** ADR-031 (`docs/adr/2026-06-17/ADR-031-configra-absorb.md`)

## Why

`KooshaPari/Configra` (created 2026-03-25) is the original config framework intent.
`KooshaPari/phenotype-config` (created 2026-06-17) was a duplicate per ADR-022 RFC 002.
**ADR-031 consolidates: `phenotype-config` → `Configra`.**

## Source

The current `phenotype-config/crates/settly/` Rust crate is the canonical config code.
It contains ~64 LoC of file-loading ports + hexagonal architecture (domain/application/adapters/infrastructure).

## Target

`KooshaPari/Configra` (rename), with `crates/settly/` as the canonical substrate.

## Migration steps (T19)

| # | Task | Repo | Status |
|---|---|---|---|
| T19.1 | Inspect `phenotype-config` contents | local | DONE |
| T19.2 | Author `MIGRATE_TO_CONFIGRA.md` (this file) | phenotype-config | DONE (this PR) |
| T19.3 | Open PR on `phenotype-config` to update README → "DEPRECATED, see Configra" | phenotype-config | PENDING |
| T19.4 | Open PR on `phenotype-config` to add CANONICAL_REDIRECT.md pointing to Configra | phenotype-config | PENDING |
| T19.5 | Open PR on `Configra` to absorb `phenotype-config/crates/settly/` | Configra | PENDING |
| T19.6 | Update SSOT.md, AGENTS.md, STATUS.md references (one-line each) | monorepo | DONE |
| T19.7 | Schedule `phenotype-config` archive for 2026-07-15 (28-day grace) | GitHub | SCHEDULED |

## What does NOT migrate

- `phenotype-config`'s GitHub Actions, hooks, secrets — these stay (separate concern)
- `phenotype-config`'s issue tracker — historical issues stay
- PR history — preserved as-is in `phenotype-config` repo (read-only after migration)

## What DOES migrate

- The `crates/settly/` Rust source code (canonical substrate per ADR-022)
- `Cargo.toml` workspace config
- `CANONICAL.md` markers (renamed)
- `SPEC.md` (will be added to Configra)

## Consequence

After T19.5 lands:
- `KooshaPari/Configra` is the **canonical** Rust config repo (with `settly` crate)
- `KooshaPari/phenotype-config` is **deprecated** (README redirect to Configra)
- `KooshaPari/Conft` (TS edge per ADR-022) is **unaffected**

L5-104.7 — T19 (Configra absorb)
