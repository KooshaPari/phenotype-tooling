# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2026-06-20 — Absorbed governance, docs, CI, and tooling from archived Apisync repo

### Added

- Governance docs migrated from [Apisync](https://github.com/KooshaPari/Apisync) under `docs/governance/`:
  `AGENTS.md`, `CLAUDE.md`, `ADR.md`, plus 5 Architecture Decision Records under `docs/governance/adr/`
  (001-hexagonal-architecture, 002-hyper-over-axum, 003-async-graphql, 004-tokio-tungstenite,
  005-criterion). Apisync's full README, STATUS, PLAN, PRD, SPEC, FUNCTIONAL_REQUIREMENTS,
  TEST_COVERAGE_MATRIX, and CHANGELOG are preserved with `.apisync.md` suffix to disambiguate
  from apikit's own `docs/SPEC.md`, `docs/FUNCTIONAL_REQUIREMENTS.md`, `docs/TEST_COVERAGE_MATRIX.md`.
- Community / code-governance files at repo root: `CODE_OF_CONDUCT.md`, `CODEOWNERS`,
  `CONTRIBUTING.md`, `SECURITY.md`, `codecov.yml`, `FUNDING.yml`, `CITATION.cff`, `LICENSE`.
- Tooling config (replaces apikit's prior versions with Apisync's more recent ones):
  `mise.toml`, `nextest.toml`, `rust-toolchain.toml`, `rustfmt.toml`, `_typos.toml`,
  `.editorconfig`, `.gitignore`, `.gitattributes`, `.env.example`, `.health-dashboard.yml`,
  `.pre-commit-config.yaml` (preserved as symlink to `../template-commons/.pre-commit-config.yaml`),
  and `.githooks/{pre-commit,pre-push}`.
- 12 CI workflows under `.github/workflows/` (original filenames preserved): `ci.yml`,
  `release.yml`, `audit.yml`, `cargo-deny.yml`, `coverage.yml`, `quality-gate.yml`, `sast.yml`,
  `scorecard.yml`, `security-deep-scan.yml`, `security-guard.yml`, `trufflehog.yml`,
  `pages-deploy.yml`.
- Apisync's docs content under apikit: `docs/index.apisync.md`, `docs/slsa.md`,
  `docs/sessions/journeys/{index.md,quick-start.md}`, `docs/sessions/stories/{index.md,hello-world.md}`,
  `docs/sessions/traceability/index.md`, `docs/research/SOTA.md`,
  `docs/governance/.vitepress/config.mts`.

### Changed

- `README.md` — added Provenance section crediting Apisync as source repo.
- `Cargo.toml` — repository / description metadata updated to reference Apisync provenance.

### Notes

- Source archive at `/tmp/apisync-final` was preserved for audit trail; no source files deleted.
- GitHub `Apisync` repo remains archived; no status change made on the source side.
- The Apisync GitHub repository can now be deleted cleanly — all in-scope content has been
  absorbed into apikit under canonical paths.
- Existing overlapping files (`deny.toml`, `.editorconfig`, `rust-toolchain.toml`, `mise.toml`,
  `cliff.toml`, `_typos.toml`, `Taskfile.yml`, `LICENSE`, `.gitignore`) were overwritten with
  Apisync's more recent versions; `.gitignore` was the only one with non-trivial differences.

## 2026-06-20 — Second-pass absorption: leftover root configs, tooling, and orphaned sources

### Added

- `VERSION` — Apisync version pin (`0.1.0`), copied verbatim from source.
- `audit_scorecard.json` — Apisync's repo audit scorecard (overall score 48 / grade D), preserved
  for historical reference (see `docs/governance/ADR.md` for the follow-up remediation roadmap).
- `.clippy.toml` — Clippy lint configuration adopted from Apisync; was missing in the first pass.
- `.config/nextest.toml` — Apisync's nextest profile config (CI, coverage, e2e profiles); mirrored
  into apikit's `.config/` layout to match source structure. The root `nextest.toml` from Apisync
  had already been absorbed in the first pass; the `.config/` copy provides the more complete
  profile set (ci / coverage / e2e).
- `sentry_config.rs` — Apisync's Sentry initialization module (`!Sentry configuration for Apisync`,
  references FR-APISYNC-SENTRY-001). Placed at repo root to match source layout; integration into
  the apikit binary requires a follow-up `mod sentry_config` in `src/main.rs` (or equivalent).
- `.agileplus/specs/001-core-setup/{spec.md,tasks.md,meta.json}` — Apisync's agile-plus spec for
  the original core-setup work package (status: `active`, priority: `P1`, created 2026-04-02).
  Preserved verbatim for traceability; meta.json's `title` still reads "Apisync - Core Setup &
  Compliance" and may be renamed to "apikit - Core Setup & Compliance" in a follow-up commit.

### Notes (legacy files)

- `Cargo.toml.apisync-legacy` — Apisync's workspace manifest preserved as-is. The active `Cargo.toml`
  was retained as the apikit-native version (with Provenance comments referencing Apisync as the
  source-of-truth repo). Differences from the legacy file: package name (`apikit` vs `apisync`),
  repository URL, description, and Provenance metadata block.
- `src/lib.rs.apisync-legacy` — Apisync's library entry point preserved as-is. The active `src/lib.rs`
  was retained (only difference is the module-level docstring: `apisync` → `apikit`); module tree,
  re-exports, and `ApiKit` placeholder struct are identical between the two files.

[Unreleased]: https://github.com/KooshaPari/apikit/compare/main...HEAD
