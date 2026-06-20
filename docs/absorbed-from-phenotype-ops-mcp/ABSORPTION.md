# Absorbed from phenotype-ops-mcp

**Source:** `KooshaPari/phenotype-ops-mcp`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-ops-mcp/`
**Tracked file count:** 86

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .editorconfig
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/dependabot.yml
    .github/workflows/ci.yml
    .github/workflows/codeql.yml
    .github/workflows/doc-links.yml
    .github/workflows/fr-coverage.yml
    .github/workflows/lint.yml
    .github/workflows/manifest-check.yml
    .github/workflows/quality-gate.yml
    .github/workflows/scorecard.yml
    .github/workflows/secrets-scan.yml
    .github/workflows/trufflehog.yml
    .gitignore
    .golangci.yml
    AGENTS.md
    CHANGELOG.md
    CLAUDE.md
    CODEOWNERS
    CONFIG.md
    CONVERGENCE_PLAN_2026_06_10.md
    FUNDING.yml
    Justfile
    LICENSE
    LICENSE-APACHE
    LICENSE-MIT
    README.md
    SECURITY.md
    Taskfile.yml
    adapters/doc.go
    adapters/registry.go
    adapters/shell.go
    audit_scorecard.json
    config.example.env
    core/contracts.go
    core/errors.go
    core/tool.go
    docs/boundary/phenotype-ops-mcp.md
    docs/index.md
    docs/intent/phenotype-ops-mcp.md
    docs/journeys/manifests/README.md
    docs/operations/iconography/SPEC.md
    docs/operations/journey-traceability.md
    docs/sessions/20260429-sladge-badge/00_SESSION_OVERVIEW.md
    docs/sessions/20260429-sladge-badge/01_RESEARCH.md
    docs/sessions/20260429-sladge-badge/02_SPECIFICATIONS.md
    docs/sessions/20260429-sladge-badge/03_DAG_WBS.md
    docs/sessions/20260429-sladge-badge/04_IMPLEMENTATION_STRATEGY.md
    docs/sessions/20260429-sladge-badge/05_KNOWN_ISSUES.md
    docs/sessions/20260429-sladge-badge/06_TESTING_STRATEGY.md
    go.mod
    go.sum
    images.go
    instances.go
    main.go
    ops.go
    other.go
    packages.go
    providers/cheap_llm/README.md
    providers/cheap_llm/bridge.go
    providers/cheap_llm/bridge_test.go
    providers/cheap_llm/cheap_llm_mcp/__init__.py
    providers/cheap_llm/cheap_llm_mcp/cache.py
    providers/cheap_llm/cheap_llm_mcp/cli.py
    providers/cheap_llm/cheap_llm_mcp/config.py
    providers/cheap_llm/cheap_llm_mcp/ledger.py
    providers/cheap_llm/cheap_llm_mcp/logging_util.py
    providers/cheap_llm/cheap_llm_mcp/providers/__init__.py
    providers/cheap_llm/cheap_llm_mcp/providers/base.py
    providers/cheap_llm/cheap_llm_mcp/providers/openai_compat.py
    providers/cheap_llm/cheap_llm_mcp/py.typed
    providers/cheap_llm/cheap_llm_mcp/retry.py
    providers/cheap_llm/cheap_llm_mcp/router.py
    providers/cheap_llm/cheap_llm_mcp/server.py
    providers/cheap_llm/pyproject.toml
    renovate.json5
    tests/smoke_test.go
    tools.json
    trufflehog.yml
    worklogs/ARCHITECTURE.md
    worklogs/GOVERNANCE.md
    worklogs/README.md
    worklogs/RESEARCH.md
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
