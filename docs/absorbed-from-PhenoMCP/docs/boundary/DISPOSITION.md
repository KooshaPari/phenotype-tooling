# PhenoMCP — Per-Module Boundary Disposition

**Status:** Approved assessment  
**Date:** 2026-06-17  
**Repo:** `KooshaPari/PhenoMCP`  
**Charter:** [`phenotype-registry/docs/rationalization/boundary-shaping.md`](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/boundary-shaping.md)  
**Audit:** [`docs/audit/BLOCK-C-AUDIT.md`](../audit/BLOCK-C-AUDIT.md)  
**Authority:** [ADR-017](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/017-mcp-polyrepo-boundaries.md), [ADR-019](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/019-mcp-runtime-implementation-deps.md)  
**Registry:** [`phenotype-registry/DOMAIN_ROLES.md`](https://github.com/KooshaPari/phenotype-registry/blob/main/DOMAIN_ROLES.md) — `connect` domain

> **Doctrine:** Stubs and scaffolds receive an owner and a migration path — not silent deletion.
> Hard delete applies only after absorption evidence and consumer manifest scan (Lane F).

---

## 1. Summary — recommended end-state

**PhenoMCP is a retired migration source**, not a canonical MCP boundary.

| Concern | Owner after disposition |
|---------|-------------------------|
| Org governance/agent/knowledge/policy/session/workflow MCP tools | **PhenoMCPServers** `servers/pheno-org/` |
| MCP framework (FastMCP transports, macros) | **PhenoFastMCP** (py), **PhenoFastMCP-go**, **PhenoFastMCP-rust**, **PhenoRMCP** |
| Fleet runtime (dispatch, argv, cheap-llm routing) | **substrate** |
| Catalog / wiring SSOT | **PhenoMCPServers** `catalog/registry.yaml` |
| Rust search/storage adapters (if kept) | **PhenoMCPServers** server deps or drop (YAGNI) |
| Auth (future) | **Authvault** — MUST NOT reimplement in this repo |
| This repository | **ARCHIVE** after migration PRs land |

**Do not** add new deployable MCP servers, runtime CLIs, or framework forks here.

---

## 2. Method

- Git tree `main` @ cee7633 (2026-06-17)
- Cross-repo compare: PhenoMCPServers `catalog/registry.yaml`, substrate runtime layout
- Prior ponytail audit: PR #157 branch (verdict updated for ADR-017)
- Registry: `phenotype-registry` sd-retire audit + `ECOSYSTEM_MAP.md`

---

## 3. Top-level modules — disposition table

| # | Module (path) | What it is | Disposition | Target repo | Rationale |
|---|---------------|------------|-------------|-------------|-----------|
| 1 | `python/src/pheno_mcp/` | FastMCP bridge — server, transport, six tool bundles | **ABSORB** | PhenoMCPServers `servers/pheno-org/` | ADR-017 implementations layer; catalog entry `pheno-org` exists |
| 2 | `python/src/pheno_mcp/tools/*` | `agent_*`, `governance_*`, `knowledge_*`, `policy_*`, `session_*`, `workflow_*` | **ABSORB** | PhenoMCPServers `servers/pheno-org/` | Org MCP surface; naming standard `<server>_<verb>_<noun>` |
| 3 | `python/tests/` | pytest suite for bridge | **ABSORB** | PhenoMCPServers `servers/pheno-org/tests/` | Migration gate for tool parity |
| 4 | `python/src/cheap_llm_mcp/` | Budget-LLM MCP adapter (removed on main) | **DONE** | substrate + PhenoMCPServers `servers/substrate/` | ADR-019; standalone repo deleted 2026-06-17 |
| 5 | `src/main.rs` + root `[[bin]]` | Phantom Rust binary (`println!`) | **DELETE** | — | No MCP transport; misleads consumers |
| 6 | `crates/pheno-meilisearch/` | Meilisearch HTTP client scaffold | **DECOMPOSE** | PhenoMCPServers adapter crate **or DELETE** | YAGNI until pheno-org needs live search |
| 7 | `crates/pheno-qdrant/` | Qdrant HTTP client scaffold | **DELETE** | — | Used as keyword store anti-pattern; ponytail #16 |
| 8 | `crates/phenotype-surrealdb/` | Misnamed in-memory skill store | **DELETE** | — | Never opens SurrealDB; ponytail #10 |
| 9 | `crates/pheno-ports/` | Hexagonal port traits + doubles | **DELETE** | HexaKit reference (if needed) | Duplicate DTOs; no production consumer |
| 10 | `crates/pheno-mcp-defs/` | `ToolDefinition` / `ToolError` types | **ABSORB** | PhenoFastMCP-rust / PhenoRMCP patterns | Framework-layer concern, not library repo |
| 11 | `crates/tool-registry/` | Manifest discovery registry | **ABSORB** | PhenoMCPServers catalog tooling | SSOT is `registry.yaml`, not in-repo registry |
| 12 | `bindings/{swift,kotlin,csharp}/` | Hand-rolled JSON-RPC clients | **DELETE** | Official per-platform MCP SDKs | ponytail #18; link from catalog only |
| 13 | `integration-tests/` | Broken protocol integration tests | **DELETE** | PhenoMCPServers e2e | Imports missing `pheno_mcp_protocol` |
| 14 | `tests/clap_ext_smoke.rs` | Upstream `clap-ext` smoke test | **DELETE** | `clap-ext` repo | Not PhenoMCP behavior |
| 15 | `docs/MCP-CATALOG.md` | Org MCP server registry (stale) | **ABSORB** | PhenoMCPServers `catalog/registry.yaml` | ADR-017 wiring SSOT |
| 16 | `docs/adr/ADR-001`–`005` | Aspirational architecture (unimplemented) | **DYNAMIC-KEEP** → slim | PhenoSpecs ADRs | Reduce to 1-paragraph stubs; ponytail #29 |
| 17 | `docs/research/`, `docs/sessions/` | SOTA research + session logs | **DYNAMIC-KEEP** | This repo until archive | Historical evidence |
| 18 | `docs/traceability.md`, `docs/SSOT.md` | FR/NFR trace links | **ABSORB** | PhenoMCPServers + AgilePlus | Active spec lifecycle moves out |
| 19 | `docs/operations/iconography/` | Unused SVG assets | **DELETE** | — | ponytail #31 |
| 20 | `docs/.vitepress/`, `package.json` | Docsite toolchain | **DYNAMIC-KEEP** | Until archive freeze | Doc-only |
| 21 | Root `go.mod` / `go.sum` | Empty Go scaffold | **DELETE** | — | No `go/` source tree |
| 22 | `.github/workflows/` | CI (rust, deny, audit, scorecard) | **DYNAMIC-KEEP** | Until archive | Freeze after migration |
| 23 | Root governance (`ADR.md`, `CHARTER.md`, `PLAN.md`, `PRD.md`, …) | Planning markdown | **DYNAMIC-KEEP** | phenotype-registry session artifacts | Trim per ponytail #28 on cut PR |
| 24 | `README.md` redirect banner | ADR-017/019 pointer | **DYNAMIC-KEEP** | This repo | Pre-archive consumer guard |
| 25 | Repo itself | Legacy MCP library host | **ARCHIVE** | phenotype-registry superseded row | After BC-3 migration + BC-4 cut |

---

## 4. Supersession map

| Retired surface | Successor | ADR | Evidence |
|-----------------|-----------|-----|----------|
| PhenoMCP Python org tools | PhenoMCPServers `pheno-org` | ADR-017 | `catalog/registry.yaml` |
| PhenoMCP as MCP framework home | PhenoFastMCP* + PhenoRMCP | ADR-017 | PhenoSpecs `specs/mcp/polyrepo-boundaries/` |
| cheap-llm-mcp (was in-tree) | substrate argv + PhenoMCPServers substrate server | ADR-019 | Removed from main cee7633 |
| McpKit (sibling retire) | PhenoFastMCP + PhenoMCPServers | ADR-017 | phenotype-registry sd-retire |

---

## 5. Execution phases

| Phase | Scope | Acceptance |
|-------|-------|------------|
| **P0** (this PR) | Disposition + audit + consolidation plan | Docs on `main` |
| **P1** | pheno-org migration PR in PhenoMCPServers | Tool parity tests green |
| **P2** | Ponytail cut (delete phantom Rust/bindings) | `python/` only or archive-empty |
| **P3** | GitHub archive + registry `ECOSYSTEM_MAP` finalize | Repo read-only |

---

## 6. Related documents

- [`docs/audit/BLOCK-C-AUDIT.md`](../audit/BLOCK-C-AUDIT.md)
- [`docs/audit/BLOCK-C-CONSOLIDATION-PLAN.md`](../audit/BLOCK-C-CONSOLIDATION-PLAN.md)
- [PhenoMCPServers catalog](https://github.com/KooshaPari/PhenoMCPServers/blob/main/catalog/registry.yaml)
- [phenotype-registry sd-retire audit](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/operations/sd-retire-audit-2026-06-17.md)
- [ADR-017 MCP polyrepo boundaries](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/017-mcp-polyrepo-boundaries.md)
