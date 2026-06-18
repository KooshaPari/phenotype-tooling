# Kwality retirement — architecture decision

**Date:** 2026-06-18
**Decision:** ARCHIVE + DELETE `KooshaPari/kwality` after this PR merges
**Verdict source:** kilo audit #144 (preserved, not deleted) →
**superseded by user directive 2026-06-18** ("we are looking to retire kwality
into a collection\absorb into a different project's arch. no new repos.")

## Background

`KooshaPari/kwality` is a **674 MB** Go service implementing an
"LLM Validation & Quality Assurance Platform" — DeepEval + Playwright MCP
+ Neo4j-backed requirements tracing. The repo's own README contains the
provenance:

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is planned, maintained, and managed exclusively by AI Agents.
> Slop issues, rough edges, and AI artifacts are expected and
> intentionally present as part of an **HITL-less / minimized AI-DD**
> metaproject focused on learning, refining, and brute-force training
> both the agents and the human operator.

The repo description on GitHub states:

> **STRICTLY DO NOT DELETE NOR UNARCHIVE - Personal Project**

kilo audit #144 (in `KooshaPari/phenotype-registry` PR #144) reviewed
kwality and concluded `PRESERVE` based on:

1. README and repo description both prohibit delete/unarchive.
2. No other repo in the fleet provides parity for the LLM/DeepEval/
   Playwright/Neo4j/Go server/Rust runtime-validator stack.
3. PR #157 had cherry-picked the branch-only CI/SBOM/SLSA artifacts to
   `phenotype-tooling/docs/absorbed-from-kwality/`, but the rest of the
   repo was preserved in place.

## Why we are retiring it now

The user directive of 2026-06-18 changed the constraint set:

> "we are looking to retire kwality into a collection\absorb into a
> different project's arch. no new repos."

Combined with the kilo cloud-agent absorption matrix (PR #144), this
authorizes:

1. **Absorb the rest of kwality** into the existing
   `phenotype-tooling/docs/absorbed-from-kwality/` collection.
2. **Archive** `KooshaPari/kwality` on GitHub (read-only marker).
3. **Delete** `KooshaPari/kwality` after 90 days of GitHub retention
   (or sooner if `delete_repo` scope is granted to the active gh token).

The README's "STRICTLY DO NOT DELETE" constraint is the prior personal
project promise. The 2026-06-18 directive authorizes override.

## Architecture retirement rationale

Kwality's stack is **not ported forward into the Phenotype fleet** because:

| Capability | Where it lives now |
|---|---|
| LLM eval/validation | `pheno-prompt-test` (Python, substrate per ADR-023) |
| Playwright browser automation | `Playwright-MCP` fleet substrate |
| Neo4j knowledge graph | not in fleet; no current consumer |
| Go server + HTTP API | `PhenoMCPServers` family (polyglot SDK pattern) |
| DeepEval adapter | replaced by `pheno-prompt-test` eval framework |
| Runtime validator (Rust) | `phenotype-otel` + `pheno-context` for runtime context |

Retiring kwality **does not lose any production capability** — every
capability is either covered by an existing substrate or has no current
consumer. The absorbed content is **research/training material** for the
HITL-less AI-DD metaproject, preserved verbatim for historical reference.

## What is preserved

All 93 non-binary, non-cache, non-media files from the main branch at
retirement time, in this directory. See [`INDEX.md`](./INDEX.md) for the
complete layout.

The compiled artifacts (25 MB binaries, 2.7 MB sqlite memory cache,
5.9 MB demo GIFs) are excluded — they are regenerable and would bloat
the tooling repo. The `demos/*.tape` VHS source scripts ARE preserved
so the GIFs can be regenerated on demand.

## What happens to the source repo

1. **Step 1: Merge this PR** — `KooshaPari/kwality` source remains
   active on GitHub but is now fully absorbed here. (May already be done.)
2. **Step 2: Archive** — `gh repo archive KooshaPari/kwality` (set
   read-only marker). Can be done by anyone with write access.
3. **Step 3: Delete** — via GitHub UI (Settings → Danger Zone → Delete
   this repository) or `gh repo delete KooshaPari/kwality --yes`
   (requires `delete_repo` scope; current token does not have it).
4. **Step 4: Tombstone** — GitHub retains the soft-delete record for
   90 days; after that, the repo is permanently destroyed.

After step 4, `KooshaPari/kwality` is fully retired. All historical
content lives in `phenotype-tooling/docs/absorbed-from-kwality/`.

## Naming convention

Other retired collections follow the `docs/absorbed-from-<source>/` pattern
(e.g., `absorbed-from-PhenoProc`, `absorbed-from-HexaKit`). The kwality
absorption extends this pattern. No code is built from these directories
— they are pure documentation/preservation surfaces.

## Manual delete command (when scope is granted)

```bash
# One-time: grant the gh token the delete_repo scope
gh auth refresh -h github.com -s delete_repo

# Then:
gh repo archive KooshaPari/kwality   # step 2
gh repo delete KooshaPari/kwality --yes   # step 3
```

Or via UI: <https://github.com/KooshaPari/kwality/settings#danger-zone>

## Refs

- kilo audit #144 — `KooshaPari/phenotype-registry` PR #144
- PR #157 — initial branch-only artifacts absorption (baseline)
- ADR-023 — app substrate placement (replaces kwality stack)
- ADRS.md (absorbed) — full architectural decision records
- findings/2026-06-17-L5-104 — migration matrix