# Absorbed from phenotype-* packages — 2026-06-18

**Sources (deleted):** `KooshaPari/phenotype-sdk`, `phenotype-bot-framework`, `phenotype-discord-adapter`, `phenotype-github-adapter`
**Target:** `KooshaPari/phenotype-tooling/docs/absorbed-from-phenotype-bots/`

These four packages were created 2026-06-18 as part of the AtomsBot decomposition (S14-S17) but were immediately superseded by the wave-3 consolidation directive. Their content is preserved here as a reference collection.

## Package Summary

### `sdk/` — @phenotype/sdk (now empty/absorbed)
- Core TypeScript types: `Adapter`, `Bot`, `Message`, `AdapterType`
- 1 file (`src/index.ts`), 0 implementation, 0 tests
- Status: superseded — the types are now inlined in each adapter

### `bot-framework/` — @phenotype/bot-framework
- `PhenotypeBot` class with adapter registration, message routing, lifecycle
- `SimpleRouter` with string + regex pattern matching
- 3 vitest tests
- Status: reusable framework pattern, see `src/index.ts`

### `discord-adapter/` — @phenotype/discord-adapter
- `DiscordAdapter` implementing the `Adapter` contract
- Translation helper: `DiscordMessageInput` → `Message`
- 4 vitest tests
- Runtime dep: `discord.js ^14.14.0`

### `github-adapter/` — @phenotype/github-adapter
- `GitHubAdapter` implementing the `Adapter` contract
- Translation helper: `GitHubEventInput` → `Message`
- 4 vitest tests
- Runtime dep: `@octokit/rest ^20.0.0`

## Why Consolidated

Per the wave-3 directive ("all 5 phenotype-* repos need to be deleted \ absorbed into another repo or collection"), these packages were not promoted to first-class substrate repos. The patterns are preserved here for reference. If/when a fleet-wide bot framework is needed, the `bot-framework/` + `discord-adapter/` + `github-adapter/` triad can be promoted to a single `phenotype-bots` package.

## Source ADRs

- ADR-023 (app substrate placement): bot adapters are framework-tier, not substrate-lib-tier
- ADR-042 (substrate graduation): bot framework did not meet SDK-tier criteria
- 71-pillar audit 2026-06-17: no bot-framework baseline existed in the fleet
