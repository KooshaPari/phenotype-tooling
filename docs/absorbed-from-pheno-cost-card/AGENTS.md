# AGENTS.md — pheno-cost-card

## Purpose

Per-repo and fleet cost card. Tracks monthly CI minutes, LLM token spend
in USD, and storage GB. Renders as 1-page markdown per repo + 1-page
fleet card aggregating all repos.

## Build & Test

```bash
just dev        # pip install -e ".[dev]"
just test       # pytest -v
```

## Repo conventions

- Standard Python src/ layout with hatchling
- `CostCard` is a frozen dataclass (immutable)
- `render.render_repo_card` and `render.render_fleet_card` are pure functions
- `collectors.*` functions read checked-in `.cost-card/*.json` ledgers
  (so the card is reproducible in CI without API access)

## Do Not Touch

- The `CostCard` dataclass fields — they're the wire format for `.cost-card/`
  JSON exports consumed by downstream dashboards.
- The `render_*` function signatures — they're called from external
  scripts (e.g. weekly fleet reports).
- Lockfiles and submodule pins: `**/Cargo.lock`, `**/package-lock.json`,
  `**/yarn.lock`, `**/pnpm-lock.yaml`, `**/poetry.lock`, `**/.gitmodules`
  (enforced by `pheno-vibecoding-guard` pre-commit hook).
- Common secrets: `**/*.pem`, `**/*.key`, `**/*.p12`, `**/secrets/**`,
  `**/.env`, `**/.envrc` (enforced by `pheno-vibecoding-guard`).

## Reference

- See `/Users/kooshapari/CodeProjects/Phenotype/repos/FLEET_100TASK_DAG_V4.md`
  §64 Side Y (Cost / Economics) and §78.6 (V13 grand-total).
- See `pheno-worklog-schema` for the related fleet-wide tracking schema.
