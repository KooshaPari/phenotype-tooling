# pheno-prompt-test

## Build & test
- Build:  `hatch build`
- Test:   `pytest`
- Lint:   `ruff check src tests`
- Audit:  `pip-audit`
- Sign:   `cosign sign-blob`

## Conventions
- Commits: Conventional Commits
- Branch:  `<layer>/<slug>-<YYYY-MM-DD>`
- WORKLOG: append 1 row to `WORKLOG.md` per V4 DAG task ID
- PRs:     reference V4 task ID in body

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
