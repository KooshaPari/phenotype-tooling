# Absorbed from pheno-mcp-router

**Source:** `KooshaPari/pheno-mcp-router` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-pheno-mcp-router/`
**Tracked file count:** 55

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .editorconfig
    .env.example
    .gitattributes
    .github/CODEOWNERS
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/config.yml
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/ISSUE_TEMPLATE/question.md
    .github/ISSUE_TEMPLATE/security_report.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/workflows/audit.yml
    .github/workflows/ci.yml
    .github/workflows/deny.yml
    .github/workflows/release.yml
    .github/workflows/scorecard.yml
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
    SPEC.md
    WORKLOG.md
    audit_scorecard.json
    deny.toml
    docs/PROVIDER_GUIDE.md
    examples/quickstart.py
    justfile
    linter-output.json
    llms.txt
    pyproject.toml
    pyrightconfig.json
    src/pheno_mcp_router/__init__.py
    src/pheno_mcp_router/adapters.py
    src/pheno_mcp_router/audit.py
    src/pheno_mcp_router/budget.py
    src/pheno_mcp_router/cli.py
    src/pheno_mcp_router/config.py
    src/pheno_mcp_router/cost.py
    src/pheno_mcp_router/cost_middleware.py
    src/pheno_mcp_router/ports.py
    src/pheno_mcp_router/quota.py
    src/pheno_mcp_router/tiers.py
    tests/test_audit.py
    tests/test_budget.py
    tests/test_cost.py
    tests/test_cost_middleware.py
    tests/test_ports.py
    tests/test_quota.py
    tests/test_smoke.py
    tests/test_tiers.py
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
