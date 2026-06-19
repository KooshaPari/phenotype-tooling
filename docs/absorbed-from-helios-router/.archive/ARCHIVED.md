# ARCHIVED

**Archived date:** 2026-06-08
**Reason:** Superseded by [OmniRoute](https://github.com/KooshaPari/OmniRoute) (canonical Phenotype routing per OmniRoute ADR-001).
**Canonical successor:** https://github.com/KooshaPari/OmniRoute

This repository is archived and read-only. It will not receive further updates, CI runs, or Pages deployments.

## Migration Notes

`helios-router` was a scaffold shell with no production routing logic. Most of the contents (Rust crates, harness, portage, electrobun, mock benchmarks) are throwaway scaffolding and should be ignored.

The **only real reusable code** in this repo lives in the dashboard sub-app:

| File | Purpose |
| --- | --- |
| `dashboard/src/components/RoutingTable.tsx` | Tabular view of routing rules (provider, model, weight, latency). |
| `dashboard/src/components/ParetoChart.tsx` | Pareto-front visualization for cost/quality tradeoffs. |
| `dashboard/src/data/mockData.ts` | Seeded mock data fixtures for the dashboard widgets (with `mockData.test.ts`). |

If you need that UI, copy those three files into a new app — do not depend on this repo. For real routing, use OmniRoute's OpenAI-compatible gateway.

See `README.md` and `docs/` for the original supersession notice.
