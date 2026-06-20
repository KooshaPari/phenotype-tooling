# Functional Requirements — phenotype-dep-guard

## FR-RES — Resolution

| ID | Requirement |
|----|-------------|
| FR-RES-001 | The system SHALL resolve direct dependencies from pip, npm, cargo, and go.mod lock files. |
| FR-RES-002 | The system SHALL resolve transitive dependencies to full depth. |
| FR-RES-003 | The system SHALL cross-reference all resolved packages against OSV and NVD databases. |
| FR-RES-004 | The system SHALL cache resolution results with a configurable TTL (default 24 h). |

## FR-TRI — Triage

| ID | Requirement |
|----|-------------|
| FR-TRI-001 | The system SHALL perform AST parsing on Python and JavaScript package source files. |
| FR-TRI-002 | The system SHALL detect install-time scripts with network or filesystem side effects. |
| FR-TRI-003 | The system SHALL assign severity levels: critical, high, medium, low, info. |
| FR-TRI-004 | The system SHALL report the specific code pattern matched for each finding. |

## FR-POL — Policy

| ID | Requirement |
|----|-------------|
| FR-POL-001 | The system SHALL read policy rules from `contracts/reconcile.rules.yaml`. |
| FR-POL-002 | The system SHALL exit with code 1 when any finding meets or exceeds the configured threshold. |
| FR-POL-003 | The system SHALL produce a SARIF-formatted report artifact on every run. |
| FR-POL-004 | The system SHALL support a `--fail-on` flag accepting `critical`, `high`, `medium`, or `low`. |

## FR-CI — CI Integration

| ID | Requirement |
|----|-------------|
| FR-CI-001 | The system SHALL provide a CLI entry point usable in GitHub Actions steps. |
| FR-CI-002 | The system SHALL post findings as GitHub Check annotations when `GITHUB_TOKEN` is present. |
| FR-CI-003 | The system SHALL support `--output-format` accepting `sarif`, `json`, and `text`. |

## FR-API — Programmatic API

| ID | Requirement |
|----|-------------|
| FR-API-001 | The system SHALL expose a Python API function `scan(path, config)` returning structured results. |
| FR-API-002 | The system SHALL emit structured trace events compatible with helix-tracing. |