# Absorbed from pheno-errors

**Source:** `KooshaPari/pheno-errors`
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-errors/`
**Tracked file count:** 34

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .editorconfig
    .gitattributes
    .github/CODEOWNERS
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/ISSUE_TEMPLATE/other.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/dependabot.yml
    .github/workflows/cargo-audit.yml
    .github/workflows/cargo-deny.yml
    .github/workflows/ci.yml
    .github/workflows/codeql-rust.yml
    .github/workflows/governance.yml
    .github/workflows/scorecard.yml
    AGENTS.md
    ARCHITECTURE.md
    CHANGELOG.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    Cargo.toml
    LICENSE
    README.md
    SECURITY.md
    SPEC.md
    cliff.toml
    default_346674147141687263_0_89374.profraw
    default_9677804025958737405_0_89374.profraw
    deny.toml
    dprint.json
    fuzz/.gitignore
    fuzz/Cargo.toml
    fuzz/fuzz_targets/app_error_display.rs
    justfile
    src/lib.rs
```

## Intentional exclusions

The following generated/runtime artifacts exist in the source working tree but are intentionally not mirrored because they are not tracked source files:

- `__pycache__/`
- `*.egg-info/`
- `target/`
- `.benchmarks/`
- `.pytest_cache/`

## Verification note

Coverage is intended to match the source repository tracked inventory exactly; any extra files in this directory are limited to this manifest and may be used for archival context.
