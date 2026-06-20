# Absorbed from pheno-scaffold-kit

**Source:** `KooshaPari/pheno-scaffold-kit`
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-scaffold-kit/`
**Tracked file count:** 44

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .editorconfig
    .gitattributes
    .github/CODEOWNERS
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/config.yml
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/ISSUE_TEMPLATE/question.md
    .github/ISSUE_TEMPLATE/security_report.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/dependabot.yml
    .github/workflows/ci.yml
    .github/workflows/doc-links.yml
    .github/workflows/fr-coverage.yml
    .github/workflows/quality-gate.yml
    .github/workflows/trufflehog.yml
    .gitignore
    .pre-commit-config.yaml
    AGENTS.md
    ARCHITECTURE.md
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
    examples/quickstart.py
    justfile
    llms.txt
    pyproject.toml
    pyrightconfig.json
    src/pheno_scaffold_kit/__init__.py
    src/pheno_scaffold_kit/_drift_detector.py
    src/pheno_scaffold_kit/_framework_lint.py
    src/pheno_scaffold_kit/_predict.py
    src/pheno_scaffold_kit/cli.py
    tests/test_absorbed_tools.py
    tests/test_detect_repo_type.py
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
