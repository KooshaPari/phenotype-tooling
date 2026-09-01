# AGENTS.md — pheno-forge-plugins

**Status:** ACTIVE (PR 1 of the 3-PR forgecode improvement sequence; ADR-096, accepted 2026-06-23)
**Bucket:** ACTIVE (per ADR-023; this is a `phenotype-*-framework` substrate, not an app)
**Owner:** thegent circle
**Refs:** `findings/2026-06-23-forgecode-improvement-plan.md`, ADR-096, ADR-023 (Rule 3.1 quality bar), ADR-040 (coverage), ADR-042B (substrate quality bar)

## What this repo is

The plugin bundle for `antinomyhq/forgecode`. Ships 6 plugins that bring up the local-first memory + config + tracing stack as per-machine sidecars, not session-bound processes. Zero code in forgecode; everything is plugin-toml + systemd + scripts.

## Stack (locked)

| Plugin | Backend | License | Endpoint |
|---|---|---|---|
| `pheno-supermemory` | `supermemoryai/supermemory` | source-available (self-host binary) | `http://127.0.0.1:3030` |
| `pheno-letta` | `letta-ai/letta` | Apache-2.0 | `http://127.0.0.1:8283` |
| `pheno-cognee` | `topoteretes/cognee` (MCP) | Apache-2.0 | stdio `cognee-mcp` |
| `pheno-mem0` | `mem0ai/mem0` | Apache-2.0 | `http://127.0.0.1:8000` |
| `pheno-config` | `KooshaPari/Configra` | Apache-2.0 (per ADR-031) | `http://127.0.0.1:9100` |
| `pheno-tracing` | `open-telemetry/opentelemetry-collector-contrib` | Apache-2.0 | OTLP gRPC `:4317` + HTTP `:4318` |

## Conventions

- **Branch naming:** `chore/<req-id>-<slug>-<date>` for chore work; `feat/<req-id>-<slug>-<date>` for features
- **Commit messages:** Conventional Commits
- **PR labels:** `governance`, `L<n>-#<n>`, `forge-improvement`
- **SOTA artifacts:** `findings/`, `plans/`, `worklogs/`, `docs/adr/<date>/` (in the meta-repo; this repo is the code)

## Per-ADR-023 Rule 3.1 quality bar (this repo satisfies it)

- **Spec** — this file + `README.md` + per-plugin `README.md` (1-page max each)
- **Docs** — `README.md` + this `AGENTS.md` + the per-plugin `SKILL.md` files
- **Test matrix** — `tests/` — bats smoke tests for all lifecycle scripts (exit codes + JSON output validation)
- **Observability** — every plugin's `pheno-*.service` is a `Type=notify` unit that exports its lifecycle to `pheno-tracing`
- **Coverage gate** — 80% per ADR-040 (script coverage measured by `bats` test suite; enforced in CI)
- **CI gate** — `.github/workflows/ci.yml` runs shellcheck + bats on every PR; `pheno-ci-templates` for full OTLP smoke test
- **Worklog v2.1** — `WORKLOG.md` uses the 7-column schema with `device:` field (per ADR-015 v2.1)

## PR 1 acceptance criteria

- [ ] 6 plugins install via `forge plugin install` from tarball
- [ ] `pheno-forge-sidecars.target` brings up all 6 services at boot
- [ ] `forge plugin info <name>` reports healthy for all 6
- [ ] Healthcheck script returns 0 + JSON status for all 6
- [ ] `systemctl status pheno-forge-sidecars.target` shows all 6 active (Linux)
- [ ] L65 SSOT lint passes (no drift between plugin.toml and systemd unit)
- [ ] macOS launchd fallback verified via `scripts/launch-sidecars.sh`

## Out of scope (deferred)

- **PR 2 (thegent-memory polyglot facade)** — separate repo + crate change; SPEC at `thegent/docs/specs/memory/v2.md`
- **PR 3 (pheno-cdylib-bridge)** — separate repo; SPEC at `thegent/docs/specs/cdylib-bridge/v1.md`
- **T3 (contribution-back to `antinomyhq/forgecode`)** — Go-side `internal/pheno/bridge.go` shim; after PR 3 lands; not a fleet PR
- **`pheno-context-engine`** — codebase RAG, the Augment gap-closer; v27 candidate
- **Eval feedback loop** — feed thegent eval infrastructure back into forgecode's eval framework; separate design session
