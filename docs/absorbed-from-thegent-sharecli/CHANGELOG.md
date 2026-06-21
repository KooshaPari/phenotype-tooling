# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Tier-0 hygiene + governance bundle (`orch-v12-s1-006`):
  - `justfile` mirroring the CI matrix (`bootstrap`, `build`, `test`, `cover`,
    `lint`, `lint-fix`, `typecheck`, `fmt`, `fmt-check`, `preflight`,
    `audit`, `deny`, `grade`, `ci`, `bump`).
  - `.github/workflows/ci.yml` rewritten from Go-flavored to Python (ruff +
    pyright + pytest 3.10/3.11/3.12 + sdist/wheel build). All third-party
    actions SHA-pinned where the SHA is known, with explicit `concurrency`
    blocks.
  - `.github/workflows/audit.yml` running `pip-audit --strict --vulnerability-service osv`
    on every push, every PR, and nightly.
  - `.github/workflows/deny.yml` running `cargo deny check`; dormant today
    and self-activates the moment a `Cargo.toml` lands at the repo root.
  - `.github/workflows/scorecard.yml` running OpenSSF Scorecard weekly +
    on push to `main`, uploading SARIF to the Code Scanning dashboard.
  - `.github/workflows/release.yml` running release-please → PyPI trusted
    publishing (OIDC) → GitHub Release, with matching `release-please-config.json`
    and `.release-please-manifest.json`.
  - `.github/CODEOWNERS` tightened with per-path ownership for release /
    supply-chain / public-API surfaces.
  - `deny.toml` (forward-looking cargo-deny config; permissive licenses
    only, OSV advisories, crates.io source).
  - `.editorconfig` (LF + UTF-8 + 4-space indent; 2-space for YAML/TOML/JSON;
    `trim_trailing_whitespace` off for Markdown).
  - `.gitattributes` (LF normalization, binary markers, linguist overrides,
    export-ignore for build / cache artefacts).

### Changed
- `.github/workflows/ci.yml` replaced (Go toolchain → Python toolchain) to
  match the actual `pyproject.toml` runtime.

## [0.1.0] - 2026-06-14

### Added

- Initial release with version tracking.

[Unreleased]: https://github.com/KooshaPari/thegent-sharecli/compare/0.1.0...HEAD
[0.1.0]: https://github.com/KooshaPari/thegent-sharecli/releases/tag/0.1.0
