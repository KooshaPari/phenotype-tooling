# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Notes
- Issue #1 ("PR 2: thegent-memory polyglot facade") was filed against this
  repo by mistake. PR 2's code lives in `KooshaPari/thegent` at
  `crates/thegent-memory/`, not here — this repo is a no-Rust plugin bundle
  (see `Cargo.toml` and `AGENTS.md` § "PR 1 acceptance criteria"). Re-routed
  via the worklog entry; no source changes in this repo. See
  `KooshaPari/thegent/issues` for the canonical PR 2 tracker.

## [0.1.0] - 2026-06-23

### Added

- Initial scaffold: 6 forgecode plugins (pheno-supermemory, pheno-letta, pheno-cognee, pheno-mem0, pheno-config, pheno-tracing)
- Per-plugin systemd units + `pheno-forge-sidecars.target` bring-up
- macOS launchd fallback via `scripts/launch-sidecars.sh`
- Generic `scripts/{spawn,teardown,healthcheck}.sh` (sourced per-plugin from `plugin.env`)
- `scripts/fetch-sidecars.sh` — downloads binaries from upstream releases
- `scripts/build-tarball.sh` — builds the install tarball
- `scripts/install.sh` — convenience installer
- Per-ADR-023 Rule 3.1: README, AGENTS, WORKLOG (v2.1 schema), CHANGELOG, llms.txt, LICENSE-MIT, LICENSE-APACHE

### Notes

- PR 1 of the 3-PR forgecode improvement sequence (ADR-096)
- PR 2 = `thegent-memory` polyglot facade (SPEC at `thegent/docs/specs/memory/v2.md`)
- PR 3 = `pheno-cdylib-bridge` (SPEC at `thegent/docs/specs/cdylib-bridge/v1.md`)
