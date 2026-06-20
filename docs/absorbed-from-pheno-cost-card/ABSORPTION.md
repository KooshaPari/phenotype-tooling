# Absorbed from pheno-cost-card

**Source:** `KooshaPari/pheno-cost-card`
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-cost-card/`
**Tracked file count:** 32

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/CODEOWNERS
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/config.yml
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/ISSUE_TEMPLATE/question.md
    .github/ISSUE_TEMPLATE/security_report.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/workflows/ci.yml
    .gitignore
    .pre-commit-config.yaml
    AGENTS.md
    CHANGELOG.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    LICENSE
    LICENSE-APACHE
    LICENSE-MIT
    README.md
    SECURITY.md
    SPEC.md
    WORKLOG.md
    audit_scorecard.json
    deny.toml
    examples/fleet_card.py
    justfile
    llms.txt
    pyproject.toml
    requirements-dev.txt
    src/pheno_cost_card/__init__.py
    src/pheno_cost_card/collectors.py
    src/pheno_cost_card/render.py
    tests/test_smoke.py
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
