# Absorbed from phenotype-py-extras

**Source:** `KooshaPari/phenotype-py-extras`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-py-extras/`
**Tracked file count:** 47

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
    docs/boundary/phenotype-py-extras.md
    docs/index.md
    docs/intent/phenotype-py-extras.md
    docs/llms-txt-spec.md
    docs/llms.txt
    docs/slsa.md
    examples/llms_txt/quickstart.py
    pyproject.toml
    pyrightconfig.json
    src/phenotype_py_extras/__init__.py
    src/phenotype_py_extras/cli.py
    src/phenotype_py_extras/llms_txt/__init__.py
    src/phenotype_py_extras/llms_txt/cli.py
    src/phenotype_py_extras/llms_txt/core.py
    src/phenotype_py_extras/mcp.py
    src/phenotype_py_extras/prompt_test/__init__.py
    src/phenotype_py_extras/prompt_test/plugin.py
    src/phenotype_py_extras/testing.py
    src/phenotype_py_extras/web.py
    tests/llms_txt/test_core.py
    tests/llms_txt/test_init.py
    tests/prompt_test/__init__.py
    tests/prompt_test/test_init.py
    tests/prompt_test/test_plugin.py
    tests/test_imports.py
    tests/test_py_utils_smoke.py
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
