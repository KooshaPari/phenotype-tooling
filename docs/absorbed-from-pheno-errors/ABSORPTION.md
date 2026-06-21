# Absorbed from pheno-errors

**Source:** `KooshaPari/pheno-errors` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-errors/`
**Tracked file count:** 16

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/CODEOWNERS
    .github/workflows/cargo-audit.yml
    .github/workflows/cargo-deny.yml
    .github/workflows/ci.yml
    .github/workflows/codeql-rust.yml
    .github/workflows/governance.yml
    AGENTS.md
    Cargo.toml
    deny.toml
    examples/otel_quickstart.rs
    justfile
    llms.txt
    llvm-cov.toml
    scripts/coverage.sh
    src/lib.rs
    src/rfc7807.rs
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
