<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/phenotype-e2e-base/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/phenotype-e2e-base?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/phenotype-e2e-base?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->
# phenotype-e2e-base

Phenotype end-to-end testing base — Playwright harness + visual regression
fixtures for the landing pages and web frontends across the org.

## Stack

- **Language:** TypeScript
- **Runner:** Playwright (chromium + firefox + webkit)
- **Visual Regression:** Playwright snapshot tests
- **Targets:** `byteport.kooshapari.com`, `phenokits.kooshapari.com`, `agileplus.kooshapari.com`, `projects.kooshapari.com`, `kooshapari.com`

## Key Commands

```bash
# Install browsers + deps
bun install

# Run full E2E suite
bun run test

# Run a single spec
bunx playwright test tests/byteport.spec.ts

# Update visual snapshots
bunx playwright test --update-snapshots
```

## File Map

| Path | Purpose |
|------|---------|
| `tests/` | Playwright test specs (one per landing site) |
| `fixtures/` | Test fixtures (auth, navigation helpers) |
| `playwright.config.ts` | Playwright config — browser matrix, timeouts, base URLs |
| `package.json` | Bun workspace declaration; depends on `phenotype-zod-schemas` |

## Quality Gate

```bash
# Full gate (matches CI)
bun install
bun run typecheck
bun run lint
bun run test
```
