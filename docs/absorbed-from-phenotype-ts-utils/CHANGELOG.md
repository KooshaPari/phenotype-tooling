# Changelog

All notable changes to `phenotype-ts-utils` are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - 2026-06-12

### Added
- Initial public release.
- 14 helpers across 6 modules:
  - `string`: `cn`, `truncate`, `slugify`
  - `date`: `formatDate` (iso/us/eu), `parseDate`, `addDays`
  - `function`: `debounce`, `throttle`
  - `object`: `deepMerge`, `deepClone`
  - `async`: `sleep`, `retry` (exponential backoff)
  - `array`: `uniqueBy`, `groupBy`
- 28 unit tests (vitest) with v8 coverage.
- TypeScript strict-mode clean, ESM-only, ES2022 target.
- ESLint 9 + Prettier 3 configured.

[0.1.0]: https://github.com/KooshaPari/phenotype-ts-utils/releases/tag/v0.1.0
[Unreleased]: https://github.com/KooshaPari/phenotype-ts-utils/compare/HEAD
