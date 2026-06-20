# pheno-cost-card

Track per-repo monthly burn in CI minutes + LLM tokens + storage. Produces a cost card in markdown for each repo, rolled up to a fleet card.

## Purpose

`pheno-cost-card` creates compact monthly cost cards for Phenotype repositories. Each repo gets a one-page markdown report, and all repo cards can be aggregated into a one-page fleet card.

Tracked inputs:

- GitHub Actions CI minutes
- LLM token spend in USD
- Repository storage in GB
- Contributors active in the reporting window

## Install

```bash
pip install pheno-cost-card
```

For local development:

```bash
pip install -e .
```

## Usage

```bash
pheno-cost-card repo /path/to/repo --month 2026-06
pheno-cost-card fleet /Users/kooshapari/CodeProjects/Phenotype/repos --month 2026-06
```

## Output

A repo card is designed to fit on one page:

```markdown
# Cost Card: example-repo

| Metric | Value |
| --- | ---: |
| CI minutes | 1,240 |
| LLM token spend | $84.12 |
| Storage | 2.4 GB |
| Contributors | 5 |

Trend: up
Computed: 2026-06-11T12:00:00Z
```

A fleet card aggregates all repository cards:

```markdown
# Fleet Cost Card

| Metric | Value |
| --- | ---: |
| Repositories | 18 |
| CI minutes | 42,100 |
| LLM token spend | $2,430.55 |
| Storage | 91.8 GB |
| Contributors | 24 |
```

## Collectors

- `gh_actions_minutes`: collects CI minutes for a repository and month.
- `lfm_token_ledger`: reads local LLM token ledger spend.
- `du_storage`: measures repository storage using disk usage.

Collectors are intentionally small and replaceable so the project can adapt to local ledgers, GitHub exports, or future billing APIs.
