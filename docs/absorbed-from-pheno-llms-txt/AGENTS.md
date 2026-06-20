# pheno-llms-txt

## Build & test
- Build:  `hatch build`
- Test:   `pytest`
- Lint:   `ruff check src tests`
- Audit:  `pip-audit`
- Sign:   `cosign sign-blob --bundle=sigstore.json`

## Conventions
- Commits: Conventional Commits (feat/fix/docs/style/refactor/perf/test/chore)
- Branch:  `<layer>/<slug>-<YYYY-MM-DD>` (e.g. `l1/l1-triage-2026-06-11`)
- WORKLOG: append 1 row to `WORKLOG.md` per V4 DAG task ID
- PRs:     reference V4 task ID in body, e.g. `Refs V4-1.2.3`

## Do-not-touch zones
- `<archive>/` (stale work, archived intentionally)
- `<vendor>/`, `<node_modules>/` (third-party)
- `**/.git`, `**/Cargo.lock` (unless explicitly updating deps)
- files marked `# DO NOT EDIT` header
- Lockfiles and submodule pins: `**/Cargo.lock`, `**/package-lock.json`,
  `**/yarn.lock`, `**/pnpm-lock.yaml`, `**/poetry.lock`, `**/.gitmodules`
  (enforced by `pheno-vibecoding-guard` pre-commit hook).
- Common secrets: `**/*.pem`, `**/*.key`, `**/*.p12`, `**/secrets/**`,
  `**/.env`, `**/.envrc` (enforced by `pheno-vibecoding-guard`).

## Ownership
- See `CODEOWNERS` (GitHub) — agents should not self-approve PRs
- Last 5 contributors: `git shortlog -sn | head -5`
