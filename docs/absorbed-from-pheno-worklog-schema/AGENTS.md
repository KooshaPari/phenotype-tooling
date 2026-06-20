# pheno-worklog-schema

> WORKLOG.md v2.1 schema parser + validator (11-column markdown table

## Build & test
- Build:  `pip install -e ".[dev]"`
- Test:   `pytest -q`
- Lint:   `ruff check . && ruff format --check .`
- Types:  `mypy src`
- Audit:  `pip-audit`
- Sign:   `cosign sign-blob` (on release)

## Conventions
- Commits:  Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`)
- Branches: `chore/<req-id>-<slug>-<date>` for chore work; `feat/<req-id>-<slug>-<date>` for features
- WORKLOG:  append 1 row per task to `WORKLOG.md` (v2.1 schema — 11 columns; `device` is required)
- PRs:      reference the v8 DAG task ID in the body (e.g. `T15.NN` from `plans/2026-06-18-v8-dag-stable.md`)

## Quality gates (ADR-023 Rule 3.1, lib/SDK)
- Test count target: 30 tests minimum (current: 30)
- Coverage gate: **80%** — 80% per ADR-023 Rule 3.1 (lib/SDK gate)
- CI workflow: `.github/workflows/ci.yml` (self-contained Python template)

## Do-not-touch zones
- `<archive>/` (stale work, archived intentionally)
- `<vendor>/`, `<node_modules>/` (third-party)
- `**/.git`, `**/Cargo.lock` (unless explicitly updating deps)
- files marked `# DO NOT EDIT` header
- `pheno-ci-templates/` paths (template lives in a separate substrate repo)

## Cross-references
- ADR-019 (settle-archive: substrate deprecation), ADR-023 (agent-effort governance), ADR-025 (worklog v2.1), ADR-030 (worklog v2.1 spec)
- `pheno-worklog-schema` (v2.1 parser), `pheno-ci-templates` (CI template, local-only)
