# Changelog — pheno-cost-card

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - 2026-06-11

### Added

- Initial scaffold from V11 prep agent design (V4 §64 Side Y).
- `CostCard` frozen dataclass: repo, ci_minutes, llm_tokens_usd, storage_gb, computed_at, contributors
- `render.render_repo_card(card, previous_total_usd)` and `render.render_fleet_card(cards, previous_total_usd)`
- 3 collectors: `gh_actions_minutes`, `lfm_token_ledger`, `du_storage`
- 2 smoke tests (repo card + fleet card)
- pyproject.toml, justfile, ci.yml, AGENTS.md, llms.txt, .gitignore
[Unreleased]: https://github.com/KooshaPari/pheno-cost-card/compare/HEAD
