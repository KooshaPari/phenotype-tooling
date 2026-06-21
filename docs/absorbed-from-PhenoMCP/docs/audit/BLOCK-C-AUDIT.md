# Block-C Audit — KooshaPari/PhenoMCP

**Date:** 2026-06-17  
**Auditor:** ecosystem disposition wave (Block-C)  
**Charter:** [`phenotype-registry/docs/rationalization/boundary-shaping.md`](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/boundary-shaping.md)  
**Authority:** [ADR-017](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/017-mcp-polyrepo-boundaries.md), [ADR-019](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/019-mcp-runtime-implementation-deps.md)  
**Registry tracker:** phenotype-registry [sd-retire audit](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/operations/sd-retire-audit-2026-06-17.md)  
**AgilePlus spec:** phenodag lane `sd-retire` (tasks `sd-retire-01`…`sd-retire-05`); charter traceability via [boundary-shaping.md](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/boundary-shaping.md) and [ADR-017](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/017-mcp-polyrepo-boundaries.md)

---

## Executive summary

| Signal | Finding |
|--------|---------|
| **Repo role (historical)** | Polyglot MCP host — Python FastMCP bridge + Rust adapter scaffolds |
| **Repo role (2026-06-17)** | **SUPERSEDED** — migration source only; do not add new MCP surfaces |
| **Canonical successors** | [PhenoMCPServers](https://github.com/KooshaPari/PhenoMCPServers) (implementations), [PhenoFastMCP*](https://github.com/KooshaPari/PhenoFastMCP) (framework), [substrate](https://github.com/KooshaPari/substrate) (runtime) |
| **cheap-llm-mcp** | **Removed from tree** on `main` (cee7633); runtime → substrate per ADR-019 |
| **Python org tools** | **Pending absorb** → `PhenoMCPServers/servers/pheno-org/` (catalog `pheno-org`) |
| **Rust workspace** | Scaffold-only — phantom root binary, broken integration tests, split crate graph |
| **Prior audit (PR #157)** | Ponytail lens valid; **consolidation verdict superseded** by ADR-017 retirement |

---

## Baseline checks (main @ 2026-06-17)

| Check | Result | Notes |
|-------|--------|-------|
| README redirect banner (ADR-017/019) | **PASS** | Lines 8–11 |
| `python -m pheno_mcp` entrypoint | **PASS** | Supported until pheno-org migration lands |
| Rust root binary (`src/main.rs`) | **FAIL** | 3-line `println!` scaffold only |
| `integration-tests/` compile | **FAIL** | Imports non-existent `pheno_mcp_protocol` |
| Workspace member consistency | **WARN** | 6 crates in `crates/`; 2 opt out via nested `[workspace]` |
| `cheap_llm_mcp` in-tree | **PASS (removed)** | Migrated out; substrate owns runtime |
| `docs/MCP-CATALOG.md` freshness | **FAIL** | Still lists retired `dispatch-mcp`, `cheap-llm-mcp` repos |
| GitHub archive flag | **FAIL** | Repo active; registry marks **superseded/archived** |
| PhenoMCPServers `pheno-org` server | **PARTIAL** | Catalog entry exists; full tool parity TBD |

---

## Stack inventory

| Layer | Tech | Maturity |
|-------|------|----------|
| Python MCP bridge | `python/src/pheno_mcp/` — FastMCP, six tool bundles | **Working** — canonical until migration |
| Rust adapters | `pheno-meilisearch`, `pheno-qdrant`, `phenotype-surrealdb` | **Scaffold** — in-memory doubles, no live-server tests |
| Rust tooling crates | `pheno-mcp-defs`, `tool-registry`, `pheno-ports` | **Scaffold** — no production consumer |
| Root binary | `src/main.rs` | **Phantom** |
| Bindings | Swift / Kotlin / C# hand-rolled JSON-RPC | **Delete candidate** — use official MCP SDKs |
| Go | Root `go.mod` empty; no `go/` tree | **Phantom** |
| Node | VitePress under `docs/` | **Doc-only** |

---

## Cross-repo boundary overlaps

| Concern | Canonical owner (ADR-017) | PhenoMCP status |
|---------|---------------------------|-----------------|
| Deployable MCP servers | **PhenoMCPServers** `servers/` | Migrate `pheno_mcp` tools → `pheno-org` |
| MCP framework (FastMCP) | **PhenoFastMCP*** forks | Do not extend in-repo Python bridge long-term |
| Fleet runtime (dispatch, argv, cheap-llm) | **substrate** | `cheap_llm_mcp` already removed |
| Catalog / wiring SSOT | **PhenoMCPServers** `catalog/registry.yaml` | `docs/MCP-CATALOG.md` → redirect |
| Auth (future) | **Authvault** | No in-repo auth; aspirational ADR-004 must cite Authvault |
| Hexagonal port traits | **HexaKit** (reference only) | `pheno-ports` duplicate — drop on cut |

---

## Ponytail lens summary (from PR #157, still valid)

37 cleanup items catalogued; **~2,100 LOC** reducible. Highlights:

- Delete phantom surfaces: root binary, broken `integration-tests/`, empty root `go.mod`, decorative bindings
- Collapse or delete Rust adapter crates (`pheno-ports` doubles, misnamed `phenotype-surrealdb`)
- Slim aspirational ADRs (`docs/adr/ADR-001`–`005`) and root markdown zoo
- Consolidate 8 overlapping hook/task-runner configs to one

Full table retained in PR [#157](https://github.com/KooshaPari/PhenoMCP/pull/157) branch; execution deferred to **Phase 2** (pre-archive cut).

---

## Consolidation verdict (updated 2026-06-17)

**Verdict: SUPERSEDE → archive after migration — not a standalone long-term repo.**

PR #157 recommended "keep standalone"; **ADR-017 (Accepted 2026-06-17)** and phenotype-registry
`sd-retire` supersede that position. PhenoMCP joins McpKit in the **retired MCP library** bucket.

| Block-C action | PhenoMCP status |
|----------------|-----------------|
| GFX SDK merge | **Not implicated** |
| Auth dedup (Authvault) | **Guard only** — no auth code in-tree; future work MUST use Authvault |
| phenoShared generic-lib rescope | **Not implicated** |
| **ADR-017 MCP polyrepo retirement** | **PRIMARY** — absorb then archive |

---

## Open items (post-audit execution)

| ID | Priority | Item | Owner | Spec trace |
|----|----------|------|-------|------------|
| BC-1 | P0 | Publish `docs/boundary/DISPOSITION.md` | This PR | `sd-retire-03` |
| BC-2 | P0 | Publish `docs/audit/BLOCK-C-CONSOLIDATION-PLAN.md` | This PR | `sd-retire-05` |
| BC-3 | P1 | Complete `pheno-org` tool migration in PhenoMCPServers | PhenoMCPServers PR | phenodag `eco-013` |
| BC-4 | P1 | Apply ponytail cut (PR #157 items) or freeze Rust surface | PhenoMCP follow-up | Block-C Phase 3 |
| BC-5 | P1 | Redirect `docs/MCP-CATALOG.md` → PhenoMCPServers catalog | PhenoMCP + registry | `sd-retire-01` |
| BC-6 | P2 | GitHub archive + `ECOSYSTEM_MAP` row final | phenotype-registry | `sd-retire-03` |
| BC-7 | P2 | Close/supersede open chore PRs (#157–#162) after disposition merge | PhenoMCP | Block-C Phase 1 |

---

## Success criteria (Block-C acceptance)

1. `docs/boundary/DISPOSITION.md` on default branch with every top-level module assigned disposition + target owner
2. Consolidation verdict aligned with ADR-017 (not standalone keep)
3. README redirect cites disposition doc
4. phenotype-registry `sd-retire-03` evidence link present
