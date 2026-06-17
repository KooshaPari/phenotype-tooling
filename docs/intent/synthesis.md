# Intent synthesis — phenotype-tooling

> Generated from prompt provenance in `prompts/`. Last updated: 2026-06-16.

## Themes (from prompts)

### Theme: Platform/tooling consolidation

**User language (paraphrase with citations):**

- "role platform/tooling" — genesis rollout directive

## Confirmed goals

1. **Own `platform/tooling` domain role** — Rust CLIs, CI federation, absorbed tools
2. **Bootstrap genesis docs from HexaKit template**

## Inferred goals

| Inferred goal | Evidence | Agent action | Validate? |
|---------------|----------|--------------|-----------|
| Absorbed subdirs stay independently buildable | README absorption table | charter in-scope | pending |
| Shell scripts decommissioned after Rust port | migration plan | review Block tier | pending |

## Recommended next actions

1. Roll `quality-gate` to consumer repos per migration plan
2. Run prompt scraper after significant sessions

## LLM grounding notes

1. Read `charter.md` before adding crates or absorbed subtrees
2. Prefer Rust CLIs over new Bash per scripting policy
