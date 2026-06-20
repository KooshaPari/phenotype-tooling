# Absorbed from pheno-llms-txt

**Source:** `KooshaPari/pheno-llms-txt`
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-llms-txt/`
**Tracked file count:** 21

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/workflows/ci.yml
    .gitignore
    .pre-commit-config.yaml
    AGENTS.md
    CHANGELOG.md
    LICENSE-APACHE
    LICENSE-MIT
    README.md
    SPEC.md
    WORKLOG.md
    deny.toml
    examples/quickstart.py
    justfile
    llms.txt
    pyproject.toml
    requirements-dev.txt
    src/pheno_llms_txt/__init__.py
    src/pheno_llms_txt/cli.py
    src/pheno_llms_txt/core.py
    tests/test_core.py
    tests/test_init.py
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
