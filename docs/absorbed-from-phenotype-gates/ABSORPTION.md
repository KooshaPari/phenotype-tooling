# Absorbed from phenotype-gates

**Source:** `KooshaPari/phenotype-gates`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-gates/`
**Tracked file count:** 19

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/workflows/ci.yml
    .github/workflows/org-gates.yml
    .gitignore
    README.md
    SPEC.md
    bench/e2e/demo.js
    bench/e2e/just-demo.sh
    bench/fixture/.github/workflows/ci.yml
    bench/fixture/gates.yml
    bin/just
    docs/adopters/focalpoint.md
    gates.yml
    justfile
    package-lock.json
    package.json
    projects/phenotype-gates.json
    src/cli.js
    src/engine.js
    test/engine.test.js
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
