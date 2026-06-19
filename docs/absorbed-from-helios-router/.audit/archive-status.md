# helios-router Archive Status — 2026-06-14

**Repo:** `/Users/kooshapari/CodeProjects/Phenotype/repos/helios-router/`
**Verdict:** To be confirmed via filesystem read.

## Recommended DEPRECATION.md (if not already archived)

```markdown
# helios-router — DEPRECATED

> **Status:** Archived 2026-06-14
> **Replacement:** [OmniRoute](https://github.com/KooshaPari/OmniRoute) (ADR-001)

## Why

helios-router was a Streamlit dashboard for Pareto analysis of LLM provider/model
selection. It has been superseded by OmniRoute, which provides:

- A unified LLM router API (`/v1/chat/completions`) for multiple providers
- Built-in Pareto frontier analysis
- Real-time cost tracking
- Production-grade observability

## Migration

| Use case | Replacement |
|---|---|
| LLM cost tracking | OmniRoute's `cost_card` |
| Pareto analysis | OmniRoute's `pareto` CLI command |
| Ledger management | OmniRoute's `ledger.db` |

## Timeline

- 2026-06-14: Archived
- 2026-09-01: Hard delete (per Phenotype-org sunset policy)
```

## Recommended README header update

```markdown
# helios-router

> ⚠️ **DEPRECATED** — Use [OmniRoute](https://github.com/KooshaPari/OmniRoute) instead.

This repo is archived. See [DEPRECATION.md](./DEPRECATION.md) for the migration path.
```

## Estimated Time

- Confirm archive status: ~5 min
- Write DEPRECATION.md (if needed): ~5 min
- Update README header: ~5 min
- **Total: ~15 min**
