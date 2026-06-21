# Block-C Consolidation Plan — KooshaPari/PhenoMCP

**Date:** 2026-06-17  
**Status:** Approved for execution  
**Audit source:** `docs/audit/BLOCK-C-AUDIT.md`  
**Disposition:** `docs/boundary/DISPOSITION.md`  
**DAG lane:** Wave D (MCP retire) + phenodag `sd-retire` side-DAG  
**AgilePlus spec:** phenodag lane `sd-retire` (tasks `sd-retire-01`…`sd-retire-05`); charter traceability via [boundary-shaping.md](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/boundary-shaping.md) and [ADR-017](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/017-mcp-polyrepo-boundaries.md)

---

## Goal

Retire PhenoMCP as a **migration source** under ADR-017: absorb the working Python
org-tool surface into PhenoMCPServers, delete phantom Rust/bindings scaffolding,
then archive the repo with redirect evidence in phenotype-registry.

**This supersedes** PR #157's "keep standalone" verdict (pre-ADR-017).

---

## Current baseline (verified main @ 2026-06-17)

| Check | Result |
|-------|--------|
| README ADR-017/019 redirect banner | PASS |
| `cheap_llm_mcp` removed from tree | PASS (substrate owns runtime) |
| `python -m pheno_mcp` functional | PASS (until migration) |
| PhenoMCPServers `pheno-org` catalog entry | PASS (partial impl) |
| `docs/boundary/DISPOSITION.md` | This PR |
| GitHub archive flag | FAIL (pending P3) |
| PR #157 verdict vs ADR-017 | STALE — updated by this plan |

---

## Phase 1 — Boundary documentation (P0)

| ID | Task | Acceptance |
|----|------|------------|
| C1.1 | Publish `docs/boundary/DISPOSITION.md` | 25-row module table |
| C1.2 | Publish `docs/audit/BLOCK-C-AUDIT.md` | Verdict = SUPERSEDE, not standalone |
| C1.3 | Publish this consolidation plan | Execution DAG documented |
| C1.4 | Link disposition from README redirect | Cross-reference present |

**Risk:** Low — docs only.

---

## Phase 2 — Capability migration (P1)

| ID | Task | Acceptance |
|----|------|------------|
| C2.1 | Port `python/src/pheno_mcp/tools/*` → `PhenoMCPServers/servers/pheno-org/` | pytest parity |
| C2.2 | Wire `plugins/phenotype-bundle/mcp.json` to migrated server only | Dogfood green |
| C2.3 | Redirect `docs/MCP-CATALOG.md` header → PhenoMCPServers catalog URL | No stale retired repos |
| C2.4 | Update phenotype-registry `ECOSYSTEM_MAP` migration note | Link to this disposition |

**Owner:** PhenoMCPServers PR — phenodag task `eco-013` ([registry migration lane](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/operations/sd-retire-audit-2026-06-17.md)).

---

## Phase 3 — Ponytail cut (P1)

Execute high-value items from PR #157 ponytail table (see audit §Ponytail lens):

| ID | Task | LOC impact |
|----|------|------------|
| C3.1 | Delete `src/main.rs`, root `[[bin]]`, phantom `go.mod` | ~20 |
| C3.2 | Delete `integration-tests/`, `bindings/`, `tests/clap_ext_smoke.rs` | ~500 |
| C3.3 | Delete or collapse `crates/*` (6 crates → 0) | ~1,200 |
| C3.4 | Slim aspirational ADRs + root markdown zoo | ~1,400 |
| C3.5 | Consolidate hook configs (`lefthook` OR `pre-commit`, not both) | ~100 |

**Net:** ~2,100 LOC reduction; repo shrinks to migration stubs or empty archive shell.

---

## Phase 4 — Archive gate (P2)

| ID | Task | Acceptance |
|----|------|------------|
| C4.1 | Close/supersede open chore PRs (#154–#162) with disposition link | No conflicting merges |
| C4.2 | GitHub archive `KooshaPari/PhenoMCP` | `isArchived: true` |
| C4.3 | phenotype-registry `sd-retire-05` audit close references disposition PR | Lane complete |
| C4.4 | phenodag `sd-retire-03` PhenoMCP row → **ARCHIVED** | DAG green |

---

## Phase 5 — Cross-repo Block-C alignment (ongoing)

Sibling MCP retire dispositions (same wave):

| Repo | State | Next action |
|------|-------|-------------|
| `McpKit` | Archived 2026-06-17 | KEEP_ARCHIVED |
| `cheap-llm-mcp` | Deleted 2026-06-17 | substrate only |
| `PhenoMCPServers` | Active SSOT | Absorb pheno-org tools |
| `substrate` | Active runtime | cheap-llm argv routing |
| `PhenoFastMCP*` | Active framework | No server dirs |
| `phenotype-registry` | sd-retire DONE | Link this disposition |

---

## Execution order (DAG)

```
C1.* (this PR)
C2.* ∥ C3.1–C3.3 (migration + cut can parallel after C1 merge)
C3.4–C3.5 (doc/hook hygiene)
C4.* (archive gate — after C2 green)
```

---

## Out of scope

- Merging PhenoMCP into GFX-SDK, phenoShared, or Authvault (not implicated)
- Re-implementing auth in-repo (Authvault guard only)
- Deleting git history or force-pushing main
- Framework fork work (belongs in PhenoFastMCP* repos)

---

## Success criteria

1. Disposition + audit + plan on `main`
2. PhenoMCP role = **superseded migration source**, not canonical MCP host
3. pheno-org tools runnable from PhenoMCPServers without `pip install` from PhenoMCP
4. Repo archived with registry evidence
