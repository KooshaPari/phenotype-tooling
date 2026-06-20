"""pheno-cost-card — SPEC

## Scope

Compute and render fleet cost cards: per-repo monthly cost (CI minutes,
storage, egress, LLM tokens) and a fleet-wide aggregate. The output is a
Markdown card suitable for pasting into the weekly health inventory or a
status dashboard.

## Public API

- `pheno_cost_card.CostCard` — frozen dataclass with fields:
  `repo`, `ci_minutes`, `storage_gb`, `egress_gb`, `llm_tokens`,
  `month` (str, ISO YYYY-MM).
- `pheno_cost_card.collectors.gh_actions_minutes(repo: Path, month: str) -> float`
  — query the GitHub Actions API for monthly minutes used.
- `pheno_cost_card.collectors.local_storage_gb(repo: Path) -> float`
  — sum `.git` size + artifacts on disk.
- `pheno_cost_card.render.render_repo_card(card: CostCard) -> str`
  — Markdown table for one repo.
- `pheno_cost_card.render.render_fleet_card(cards: list[CostCard]) -> str`
  — Markdown table for the fleet aggregate.

## Conventions

- **When to use:** weekly health inventory, monthly cost retros.
- **When NOT to use:** production billing (use the platform-native exporter).
- **5-line quickstart:**
  ```python
  from pheno_cost_card import CostCard, render_fleet_card
  cards = [CostCard(repo="pheno-config", ci_minutes=120.0, ...)]
  print(render_fleet_card(cards))
  ```

## Quality bar

- 71-pillar score: 22/71 (Tier 0)
- Test matrix: 5 unit tests (smoke + per-collector + render)
- CI: pytest on push
- License: dual (MIT + Apache-2.0)

## See also

- L6 fleet health inventory
- ADR-024 (71-pillar framework)
- ADR-039 (pheno-flake template)
"""