# `phenotype-config` — DEPRECATED

**This repository is DEPRECATED as of 2026-06-17. Please use [`KooshaPari/Configra`](https://github.com/KooshaPari/Configra) instead.**

## Why deprecated

Per [ADR-031](https://github.com/KooshaPari/repos/blob/main/docs/adr/2026-06-17/ADR-031-configra-absorb.md), `Configra` (created 2026-03-25) is the canonical Rust config repo. This `phenotype-config` repo (created 2026-06-17) duplicated the intent; ADR-031 supersedes ADR-022's two-crate naming split and consolidates the canonical Rust config code into `Configra`.

## Where the code went

| Concern | New location |
|---|---|
| Rust source (`crates/settly/`) | [`KooshaPari/Configra:feat/settly-crate-absorption`](https://github.com/KooshaPari/Configra/pull/44) |
| Hexagonal architecture | `Configra/crates/settly/` (domain/application/adapters/infrastructure) |
| File-loading ports | `Configra/crates/settly/src/application/ports/` |
| TOML/JSON adapters | `Configra/crates/settly/src/adapters/` |
| ConfigError + ConfigKitError | `Configra/crates/settly/src/domain/error.rs` |
| TS edge (was: this repo's sister, `Conft`) | [`KooshaPari/Conft`](https://github.com/KooshaPari/Conft) — **unaffected** (per ADR-022) |

## What stays here

- The historical commit log (3bd48cb, 599d37d) — preserved for reference
- `MIGRATE_TO_CONFIGRA.md` — the migration plan
- `CANONICAL_REDIRECT.md` — canonical redirect notice
- The 28-day archive grace period (2026-07-15)

## Timeline

| Date | Action |
|---|---|
| 2026-06-17 | ADR-031 accepted, this repo marked DEPRECATED |
| 2026-06-17 | Configra PR #44 opened (settly crate absorb) |
| 2026-07-15 | `phenotype-config` archived (28-day grace) |

## See also

- [ADR-031](https://github.com/KooshaPari/repos/blob/main/docs/adr/2026-06-17/ADR-031-configra-absorb.md) — full decision rationale
- [ADR-022](https://github.com/KooshaPari/repos/blob/main/docs/adr/2026-06-15/ADR-022-config-consolidation-two-crate-split.md) — superseded by ADR-031
- [`MIGRATE_TO_CONFIGRA.md`](./MIGRATE_TO_CONFIGRA.md) — migration plan
- [`CANONICAL_REDIRECT.md`](./CANONICAL_REDIRECT.md) — canonical redirect

L5-104.7 — T19.3 (phenotype-config deprecation notice)
