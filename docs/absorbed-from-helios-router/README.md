# helios-router

> **Work state:** ARCHIVED · **Progress:** `██████████ 100%` (archived)
> **Archived:** 2026-06-14 · **Superseded by:** [OmniRoute](https://github.com/KooshaPari/OmniRoute) (OmniRoute ADR-001)

This repository is **archived and read-only**. All historical source, configs, assets, and tooling have been moved into [`.archive/`](./.archive/). No further development will occur here.

## What happened to the contents

Every top-level entry that used to live at the repo root — including all tracked source, build configs, CI workflows, the dashboard sub-app, scratch directories, dependency caches, and the previous `README.md` / `ARCHIVED.md` notes — has been relocated into the `.archive/` directory at the root of this repo. Nothing was deleted; everything is recoverable from git history at any time.

The repo root now contains only:

| Path | Purpose |
| --- | --- |
| `.archive/` | All former repo contents (frozen, read-only reference). |
| `.audit/` | Internal archive-status worklog. |
| `.git/` | Git history (preserved). |
| `README.md` | This file. |

`.git/` and `.audit/` were intentionally kept in place per the archival policy.

## Active work

**See [helios-cli](https://github.com/KooshaPari/helios-cli) for active work.** `helios-router` was a scaffold shell with no production routing logic. The canonical Phenotype routing layer is [OmniRoute](https://github.com/KooshaPari/OmniRoute), which provides the OpenAI-compatible gateway plus built-in Pareto / cost / ledger analysis. For the CLI surface that drives it, use `helios-cli`.

## Migration

If you previously copied files out of `helios-router`, the only real reusable UI code lives in `.archive/dashboard/src/components/RoutingTable.tsx`, `.archive/dashboard/src/components/ParetoChart.tsx`, and `.archive/dashboard/src/data/mockData.ts` (+ `mockData.test.ts`). Copy those into a new app if you still need them — do not depend on this repo.

For real routing, use OmniRoute's `/v1/chat/completions` endpoint. There is nothing here worth forking.
