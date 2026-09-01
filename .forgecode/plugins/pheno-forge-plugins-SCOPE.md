# SCOPE.md — pheno-forge-plugins

This document declares the **intentional scope boundaries** of this repository.
Pillars scored `0.0` in automated audits are by design, not omission.

## In scope

| Area | Covered by |
|------|-----------|
| Plugin packaging (6 forgecode plugins) | `plugins/` — each has `plugin.toml`, `SKILL.md`, `plugin.env`, systemd unit |
| Generic lifecycle scripts | `scripts/{spawn,teardown,healthcheck,install,fetch-sidecars,build-tarball,launch-sidecars}.sh` |
| Systemd orchestration | `systemd/pheno-forge-sidecars.target` + per-plugin `.service` units |
| Test harness | `tests/` — bats smoke tests for lifecycle scripts |
| CI (basic) | `.github/workflows/ci.yml` — shellcheck + bats |
| Release artifacts | `scripts/build-tarball.sh` → SHA256-checksummed tarball |

## Out of scope (intentional)

These absences are **design decisions**, not gaps:

| Pillar | Score | Rationale |
|--------|-------|-----------|
| L3 Data model / state | 0.0 | State is delegated to external daemons (supermemory, letta, cognee, mem0, Configra, otel-collector). This repo is an integration bundle, not a service. |
| L4 Async / event-driven I/O | 0.0 | Lifecycle is synchronous shell orchestration (systemd or background processes). Async patterns belong in the sidecar backends, not in the install/healthcheck/teardown shell layer. |
| L9/L10 Build/Release CI | 0.0 → 2.0 (this PR) | CI is delegated to `pheno-ci-templates` per AGENTS.md. A minimal CI workflow (shellcheck + bats) is added in this PR to close the feedback gap. Full build/release automation is deferred to when the sidecar binaries are built in-repo (future PR). |
| L16 i18n | 0.0 | This repo has no user-facing UI text strings. All output is operational JSON or stderr. i18n would add complexity with zero benefit for a systemd-integration bundle. |
| L17 Accessibility | N/A | No interactive web/app UI surface in this repo. |
| L20 Threat model | 0.0 | The attack surface is localhost-only (sidecars bind to 127.0.0.1). Threat modeling belongs at the sidecar application level, not the plugin wrapper. |
| L21 AuthN/Z | 0.0 | Sidecars bind to localhost only. Authentication is a no-op when the transport is loopback + systemd isolation. Individual sidecar applications may add auth independently. |
| L22 Crypto/key custody | 0.0 | No secrets or keys are managed in this repo. Plugin config is env-file-based per ADR-027; secret management is deferred to the sidecar applications. |
| L23 Audit/compliance log | 0.0 | Operational audit is handled by the sidecar backends and systemd journal. This repo is deployment scaffolding; a centralized audit trail belongs in the forgecode session layer or `pheno-tracing` OTLP pipeline. |
| L33 PR/Issue/GitOps process | 0.0 → 1.0 (this PR) | Minimal `.github/` governance (CODEOWNERS, PR template) added in this PR. Full GitOps (branch protection, required reviews, auto-merge) belongs in the org-level ruleset, not a per-repo duplication. |
| L36 Quality polish/QOL | 0.0 | No `--format json`, man pages, or completions: this is a systemd plugin bundle, not an end-user CLI tool. `healthcheck.sh` already emits JSON. |

## When this scope changes

If a future PR adds:
- First-party Rust/Go binary code → L3 (data model), L9/L10 (CI), L21 (authn) become relevant and must be addressed in the same PR.
- User-facing CLI with interactive output → L16 i18n, L36 QOL become relevant.
- Network-exposed endpoints → L20 threat model, L21 authn/z, L22 crypto become blocking.

Until then, declare scope by decision, not by absence.
