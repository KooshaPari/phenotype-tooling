# Absorbed from phenotype-request-id

**Source:** `KooshaPari/phenotype-request-id`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-request-id/`
**Tracked file count:** 31

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
    .github/dependabot.yml
    .github/workflows/ci.yml
    .github/workflows/release-attestation.yml
    .github/workflows/scorecard.yml
    .gitignore
    AGENTS.md
    CHANGELOG.md
    CLAUDE.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    LICENSE
    README.md
    SECURITY.md
    audit_scorecard.json
    docs/index.md
    docs/slsa.md
    pyproject.toml
    pyrightconfig.json
    src/phenotype_request_id/__init__.py
    src/phenotype_request_id/context.py
    src/phenotype_request_id/fastapi.py
    src/phenotype_request_id/logging.py
    tests/test_context.py
    tests/test_middleware.py
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
