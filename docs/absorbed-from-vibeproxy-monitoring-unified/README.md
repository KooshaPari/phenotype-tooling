# vibeproxy-monitoring-unified

Unified monitoring configuration for VibeProxy services. This repository is the
governance and specification home for shared VibeProxy observability assets.

## Status

Scaffolding only. No monitoring dashboards, alert rules, SDKs, or deployable
runtime configuration are checked in yet. The current repo contains governance,
tooling configs, and the specification document that will guide future
monitoring configuration.

## Scope

`vibeproxy-monitoring-unified` is intended to standardize monitoring and health
signals across VibeProxy services:

- Shared monitoring configuration and dashboard ownership.
- Alert definitions for VibeProxy service health and dependency failures.
- Consistent liveness, readiness, and startup semantics for service probes.
- Prometheus and Grafana surfaces for probe latency, availability, and error
  budget tracking.
- Documentation for routing repo-specific findings into the local worklog.

## Current Layout

| Path | Purpose |
|------|---------|
| `SPEC.md` | Specification: scope and intended contents |
| `AGENTS.md` | Agent governance |
| `CLAUDE.md` | Claude Code project instructions |
| `FUNCTIONAL_REQUIREMENTS.md` | Functional requirements tracker |
| `cliff.toml` | git-cliff changelog config |
| `mise.toml` | mise tool-version config |
| `.pre-commit-config.yaml` | pre-commit hooks |
| `.editorconfig` | Editor config |
| `CODE_OF_CONDUCT.md` | Participation expectations |
| `CONTRIBUTING.md` | Contribution workflow |
| `SECURITY.md` | Private vulnerability reporting guidance |
| `docs/worklogs/README.md` | Canonical worklog index |
| `docs/worklogs/worklog.md` | Detailed work audit log |

## Quick Start

```bash
git clone https://github.com/KooshaPari/vibeproxy-monitoring-unified.git
cd vibeproxy-monitoring-unified
mise install
pre-commit install
```

Review the intended monitoring scope:

```bash
cat SPEC.md
cat docs/worklogs/README.md
```

## Future Implementation Targets

The repository should add concrete assets only after the target VibeProxy
service inventory and ownership model are confirmed. Expected additions include:

- Dashboard definitions for service health and latency.
- Alert rules for unhealthy probes, dependency degradation, and error budgets.
- Example Kubernetes and Docker health-check configuration.
- Prometheus recording rules for normalized probe metrics.
- Integration documentation for VibeProxy service maintainers.

## Governance

Record repo-specific findings in `docs/worklogs/worklog.md`. Use parent
Phenotype governance and worklog surfaces only for cross-repo aggregation or
org-level decisions.

All future monitoring assets should include:

- Clear owning service or platform surface.
- Test or validation command where applicable.
- Alert severity and routing assumptions.
- Rollback or disablement guidance for noisy checks.

## Links

- Canonical repo: https://github.com/KooshaPari/vibeproxy-monitoring-unified
