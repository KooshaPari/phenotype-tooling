# Absorbed from PhenoAgent

**Source:** `KooshaPari/PhenoAgent` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-PhenoAgent/`
**Tracked file count:** 135

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .editorconfig
    .gitattributes
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/PULL_REQUEST_TEMPLATE.md
    .github/dependabot.yml
    .github/workflows/cargo-deny.yml
    .github/workflows/codeql.yml
    .github/workflows/doc-links.yml
    .github/workflows/fr-coverage.yml
    .github/workflows/journey-gate.yml
    .github/workflows/quality-gate.yml
    .github/workflows/scorecard.yml
    .github/workflows/trufflehog.yml
    .gitignore
    .pre-commit-config.yaml
    ADR.md
    AGENTS.md
    CHANGELOG.md
    CHARTER.md
    CITATION.cff
    CLAUDE.md
    CLIProxyAPI/sdk/cliproxy/auth/auth.go
    CLIProxyAPI/sdk/cliproxy/auth/types.go
    CODEOWNERS
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    FUNCTIONAL_REQUIREMENTS.md
    FUNDING.yml
    LICENSE
    PLAN.md
    PRD.md
    README.md
    SECURITY.md
    Taskfile.yml
    agentapi/docs/adr/ADR-001.md
    agentapi/docs/adr/ADR-002.md
    agentapi/docs/adr/ADR-003.md
    agentapi/docs/research/SOTA.md
    audit_scorecard.json
    deny.toml
    docs/adr/001-architecture-approach.md
    docs/adr/002-technology-selection.md
    docs/adr/003-data-storage-strategy.md
    docs/adr/004-api-design-strategy.md
    docs/adr/005-security-model.md
    docs/boundary/PhenoAgent.md
    docs/index.md
    docs/intent/PhenoAgent.md
    docs/journeys/manifests/main-flow.json
    docs/operations/iconography/SPEC.md
    docs/operations/iconography/fluent/alert-triangle.svg
    docs/operations/iconography/fluent/branch.svg
    docs/operations/iconography/fluent/build.svg
    docs/operations/iconography/fluent/chart-bar.svg
    docs/operations/iconography/fluent/clock.svg
    docs/operations/iconography/fluent/dashboard.svg
    docs/operations/iconography/fluent/database.svg
    docs/operations/iconography/fluent/deploy.svg
    docs/operations/iconography/fluent/file.svg
    docs/operations/iconography/fluent/folder.svg
    docs/operations/iconography/fluent/home.svg
    docs/operations/iconography/fluent/key.svg
    docs/operations/iconography/fluent/package.svg
    docs/operations/iconography/fluent/plugin.svg
    docs/operations/iconography/fluent/search.svg
    docs/operations/iconography/fluent/settings.svg
    docs/operations/iconography/fluent/shield.svg
    docs/operations/iconography/fluent/terminal.svg
    docs/operations/iconography/fluent/user.svg
    docs/operations/iconography/fluent/workflow.svg
    docs/operations/iconography/icons.svg
    docs/operations/iconography/material/alert-triangle.svg
    docs/operations/iconography/material/branch.svg
    docs/operations/iconography/material/build.svg
    docs/operations/iconography/material/chart-bar.svg
    docs/operations/iconography/material/clock.svg
    docs/operations/iconography/material/dashboard.svg
    docs/operations/iconography/material/database.svg
    docs/operations/iconography/material/deploy.svg
    docs/operations/iconography/material/file.svg
    docs/operations/iconography/material/folder.svg
    docs/operations/iconography/material/home.svg
    docs/operations/iconography/material/key.svg
    docs/operations/iconography/material/package.svg
    docs/operations/iconography/material/plugin.svg
    docs/operations/iconography/material/search.svg
    docs/operations/iconography/material/settings.svg
    docs/operations/iconography/material/shield.svg
    docs/operations/iconography/material/terminal.svg
    docs/operations/iconography/material/user.svg
    docs/operations/iconography/material/workflow.svg
    docs/operations/journey-traceability.md
    docs/research/SOTA-domain-technology-landscape.md
    docs/research/SOTA-implementation-patterns.md
    justfile
    pheno-cli/docs/adr/ADR-001-architecture-overview.md
    pheno-cli/docs/adr/ADR-002-technology-stack.md
    pheno-cli/docs/adr/ADR-003-data-persistence.md
    pheno-cli/docs/adr/ADR-004-error-handling.md
    pheno-cli/docs/adr/ADR-005-integration-api.md
    phenotype-agent-core/docs/adr/ADR-001-architecture-overview.md
    phenotype-agent-core/docs/adr/ADR-002-technology-stack.md
    phenotype-agent-core/docs/adr/ADR-003-data-persistence.md
    phenotype-agent-core/docs/adr/ADR-004-error-handling.md
    phenotype-agent-core/docs/adr/ADR-005-integration-api.md
    phenotype-agent-core/docs/research/SOTA.md
    phenotype-daemon/Cargo.toml
    phenotype-daemon/PLAN.md
    phenotype-daemon/PRD.md
    phenotype-daemon/README.md
    phenotype-daemon/SPEC.md
    phenotype-daemon/VERSION
    phenotype-daemon/docs/adr/ADR-001-architecture-overview.md
    phenotype-daemon/docs/adr/ADR-002-technology-stack.md
    phenotype-daemon/docs/adr/ADR-003-data-persistence.md
    phenotype-daemon/docs/adr/ADR-004-error-handling.md
    phenotype-daemon/docs/adr/ADR-005-integration-api.md
    phenotype-daemon/docs/adrs/ADR-001-transport-protocol.md
    phenotype-daemon/docs/adrs/ADR-002-serialization-format.md
    phenotype-daemon/docs/adrs/ADR-003-process-lifecycle.md
    phenotype-daemon/docs/research/DAEMON_SYSTEMS_SOTA.md
    phenotype-daemon/shims/csharp/PhenotypeClient.cs
    phenotype-daemon/shims/python/phenotype_shim.py
    phenotype-daemon/shims/typescript/client.ts
    phenotype-daemon/shims/typescript/package.json
    phenotype-daemon/src/main.rs
    phenotype-daemon/src/protocol.rs
    phenotype-daemon/src/rpc.rs
    phenotype-skills/Cargo.toml
    phenotype-skills/src/lib.rs
    rust-toolchain.toml
    trufflehog.yml
    worklog.md
    worklogs/2026-06-05-fleet-readiness.md
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
