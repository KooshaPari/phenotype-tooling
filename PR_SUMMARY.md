## What this consolidates

This branch consolidates multiple work-in-progress streams into a single integration branch:

- **Traceability & docs**: Adds requirement-to-code traceability matrices (`docs/traceability/`) and feature-level traceability documentation.
- **Quality gates**: Merges `wip/quality-gate-taskfile-polish` — Taskfile-driven quality gate automation, pre-commit hooks, and CI health checks.
- **Changelog tooling**: Upgrades to git-cliff v2 template with BREAKING suffix support.
- **AI-DD metadata**: Adds AI-Agent-Only repository badges and metadata blocks.

## Tests

- `cargo check --workspace` passes for all workspace members.
- `task quality-gate` (Taskfile-driven) runs pre-commit, doc-link-check, commit-msg-check, and legacy-scan.
- `cargo test --workspace` covers: `acceptance-contract`, `dag-scheduler`, `docs-health`, `fr-trace`, `quality-gate`, `legacy-scan`, `agent-orchestrator`, `audit-privacy`, `bench-guard`, `commit-msg-check`, `doc-link-check`, `fr-coverage`, `release-cut`, `sbom-gen`, `fuzz-setup`, `anthropic-usage-poll`, `agent-forecast`.

## Traceability

| Requirement | Code / Doc Location |
|---|---|
| REQ-TRACE-001: Requirement-to-code mapping | `docs/traceability/matrix.md` |
| REQ-TRACE-002: Feature-level traceability | `docs/traceability/features.md` |
| REQ-QG-001: Automated quality gates | `Taskfile.yml`, `crates/quality-gate/` |
| REQ-DOC-001: Doc health & link checking | `crates/doc-link-check/`, `crates/docs-health/` |
| REQ-REL-001: Release automation | `crates/release-cut/`, `cliff.toml` |

## Build status

- **Rust toolchain**: stable (workspace resolver = "2")
- **CI**: GitHub Actions workflows present (`.github/workflows/`)
- **Pre-commit**: `.pre-commit-config.yaml` active
- **Lockfile**: `Cargo.lock` committed

## Merge risk

| Risk | Level | Mitigation |
|---|---|---|
| git-cliff v2 template (BREAKING suffix) | Medium | Verify `CHANGELOG.md` generation before next release cut |
| New traceability docs | Low | Docs-only; no runtime impact |
| Quality-gate Taskfile changes | Low | Backward-compatible task names retained |
| Workspace crate additions | Low | `cargo check --workspace` clean |
