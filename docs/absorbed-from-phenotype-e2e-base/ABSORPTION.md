# Absorbed from phenotype-e2e-base

**Source:** `KooshaPari/phenotype-e2e-base`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-e2e-base/`
**Tracked file count:** 26

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/workflows/ci.yml
    .gitignore
    AGENTS.md
    COVERAGE.md
    COVERAGE_REPORT.md
    LICENSE-APACHE
    LICENSE-MIT
    README.md
    STATUS.md
    Taskfile.yml
    audit_scorecard.json
    bun.lock
    coverage-suite/coverage.config.ts
    coverage-suite/generate-report.ts
    coverage.json
    fixtures/index.ts
    package-lock.json
    package.json
    playwright.config.ts
    tests/agileplus.spec.ts
    tests/byteport.spec.ts
    tests/kooshapari.spec.ts
    tests/phenokits.spec.ts
    tests/phenotype-ts-utils.spec.ts
    tests/projects.spec.ts
    tsconfig.json
```

## Intentional exclusions

The following generated/runtime artifacts exist in the source working tree but are intentionally not mirrored because they are not tracked source files:

- `__pycache__/`
- `*.egg-info/`
- `target/`
- `.benchmarks/`
- `.pytest_cache/`
- `node_modules/`

## Verification note

Coverage is intended to match the source repository tracked inventory exactly; any extra files in this directory are limited to this manifest and may be used for archival context.
