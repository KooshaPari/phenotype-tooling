# Absorbed from pheno-worklog-schema

**Source:** `KooshaPari/pheno-worklog-schema`
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-worklog-schema/`
**Tracked file count:** 41

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
    .github/workflows/v21-validate.yml
    .gitignore
    AGENTS.md
    CHANGELOG.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    LICENSE
    LICENSE-APACHE
    LICENSE-MIT
    README.md
    SECURITY.md
    SPEC-v2.1.md
    SPEC.md
    WORKLOG.md
    audit_scorecard.json
    conftest.py
    deny.toml
    examples/quickstart.py
    justfile
    llms.txt
    migrate_v2_to_v2_1.py
    pyproject.toml
    pyrightconfig.json
    src/pheno_worklog_schema/__init__.py
    src/pheno_worklog_schema/cli.py
    src/pheno_worklog_schema/emit_jsonl.py
    src/pheno_worklog_schema/schema.py
    tests/test_emit_jsonl.py
    tests/test_init.py
    tests/test_migrate_v2_to_v2_1.py
    tests/test_schema.py
    tests/test_validate_worklog.py
    validate_worklog.py
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
