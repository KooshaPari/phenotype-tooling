# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository hygiene bootstrap: `SECURITY.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `CHANGELOG.md` (per audit #206).
- T0 governance audit: `T0-AUDIT-2026-06-08.md` recording the 14-axis governance score (11 green, 3 yellow, 0 red → 89%), charter reminder, and a list of drift items surfaced during the audit.
- 14-axis governance snapshot appended to `STATUS.md` (mirrors the audit document so a reader of either file sees the same score).

### Changed
- `STATUS.md` extended with a `## T0 audit (2026-06-08)` section, without disturbing the existing D7/D8 history.

### Deprecated

### Removed

### Fixed
- `AGENTS.md`: replaced corrupted commit (invalid UTF-8, CRLF line endings, embedded HTML entity, control character) with the canonical clean version aligned with the docs-only PRD constraint.

### Security
- T0 audit confirms `.github/workflows/trufflehog.yml` is the single source of secret-scanning truth; no `gitleaks.toml` is present in this hub (Trufflehog is the org's choice per `SECURITY.md:28`).

[Unreleased]: https://github.com/KooshaPari/phenoXdd/compare/HEAD...HEAD
