# Changelog

All notable changes to Paginary will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.0.1] - 2026-04-24

### Added

- **Initial Bootstrap**: VitePress 1.6+ monorepo scaffold with Bun workspaces
- **Four Apps**: handbook, specs, xdd, journeys sub-packages
- **Shared Theme**: `paginary-theme` with impeccable CSS baseline, Inter/JetBrains Mono fonts
- **Build Orchestration**: Turbo config for parallel builds
- **Documentation**: README.md, CONSOLIDATION.md mapping source repos
- **Configuration**: Root vitepress.config.ts with federated nav and sidebar
- **AGENTS.md**: AI agent instructions for Paginary development
- **CLAUDE.md**: Claude Code instructions and governance

### Status

- All sub-apps scaffolded and build-ready
- Ready for content pull from source repositories
- Local dev environment verified (`bun install && bun run build`)

### Notes

- Content from source repos (PhenoHandbook, PhenoSpecs, phenoXdd, phenotype-journeys) will be copied (not moved) into corresponding apps
- phenotype-auth-ts flagged for evaluation as potential documentation subject
- Deployment target: `https://phenotype.dev/paginary`
[Unreleased]: https://github.com/KooshaPari/Paginary/compare/HEAD
