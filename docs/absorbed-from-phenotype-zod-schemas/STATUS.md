# Status

## Stage 0 — State Unification

- [x] Local-only repo, no GitHub remote
- [x] Org-standard `AGENTS.md` added
- [x] Org-standard `STATUS.md` added
- [x] Dual licensing (MIT + Apache-2.0) added
- [x] `Taskfile.yml` SSOT recipes added
- [x] CI workflow on `main` branch

## Stage 1 — Tooling Standardization

- [x] TypeScript strict mode
- [x] Vitest unit test runner
- [x] Biome lint (lightweight, fast)
- [x] Bun package manager

## Stage 2 — Hexagonal / Layer Refactor

- [x] Single library crate — no port/adapter split needed (it's a
  contract-definition crate, not a port implementation)

## Stage 3 — QA Hardening

- [x] Test suite covers all 5 exported schemas
- [x] CI runs on PR + push to `main`
- [x] TruffleHog secrets scan in CI

## Next Steps

- Push to GitHub (Wave 2)
- Add to org `phenotype-registry` ECOSYSTEM_MAP.md
- Publish to internal npm registry when available
- Add per-schema Zod refinement tests (currently only happy-path)
