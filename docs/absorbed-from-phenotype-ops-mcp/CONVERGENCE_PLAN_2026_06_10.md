# MCP Convergence Plan — `phenotype-ops-mcp` (2026-06-10)

**Status**: Proposal / Phase 0 (read-only inventory)  
**Source audit**: `findings/agent-wave1-2026-06-10/05-dup-scan.md`  
**Trigger**: User directive 2026-06-10: "cheap-llm-mcp as a project needs to be merged/consumed into another project. same goes for other items."

## TL;DR

Make **`phenotype-ops-mcp`** the canonical MCP host. Absorb:

| Source | Target in `phenotype-ops-mcp` | Type | Action |
|---|---|---|---|
| `cheap-llm-mcp/src/cheap_llm_mcp/` | `providers/cheap_llm/` (Go bridge + py bridge) | Python+Go | Move + Go wrapper |
| `cheap-llm-mcp-deprecate/` | (none) | deprecated | Delete after diff |
| `cheap-llm-mcp-t1-19/` | (none) | task iteration | Delete after diff |
| `dispatch-mcp/src/dispatch_mcp/` | `tools/dispatch/` (consume via `thegent-dispatch`) | Python+Go | Move + Go wrapper |
| `dispatch-mcp-t1-0` through `t1-5` | (none) | task iterations | Delete after diff |
| `phenotype-ops-mcp-t0`, `t1-11` through `t1-14` | (none) | task iterations | Delete after diff |
| `phenotype-org-audits/` | `data/audit_fixtures/` (schema only) | fixtures | Keep as data |
| AgilePlus audit patterns | (none — stay in AgilePlus) | data | Keep in AgilePlus |

## Repo Status

| Repo | Lang | Status | Action |
|---|---|---|---|
| `phenotype-ops-mcp/` | Go (`go.mod`) | Active, has AGENTS.md, CODEOWNERS, FUNDING.yml | **CANONICAL HOST** |
| `cheap-llm-mcp/` | Python (`pyproject.toml`, v0.4.0) | Active, has fastmcp>=2.0 | **MERGE** |
| `cheap-llm-mcp-deprecate/` | Python | Stale 2026-06-08 | **DELETE** |
| `cheap-llm-mcp-t1-19/` | Python | Stale 2026-06-08 | **DELETE** |
| `dispatch-mcp/` | Python (`pyproject.toml`, v0.1.0) | Active, Apache-2.0 | **MERGE** |
| `dispatch-mcp-t1-0` through `t1-5` | Python | Stale | **DELETE** |
| `phenotype-org-audits/` | unknown | schema/references | **KEEP as data** |

## Architecture Target

```
phenotype-ops-mcp/                   # Go host (canonical)
├── go.mod
├── main.go                          # MCP server entry
├── providers/
│   ├── cheap_llm/                   # Go wrapper around cheap-llm-mcp Python (CGO or HTTP)
│   │   ├── provider.go
│   │   └── pybridge/                # Calls Python subprocess for cost/router logic
│   └── dispatch/                    # Consumes thegent-dispatch lib
│       └── dispatch.go
├── tools/
│   ├── audit/                       # Repo audit (existing)
│   ├── ops/                         # Ops operations (existing)
│   └── report/                      # Report emission (existing)
├── data/
│   ├── audit_fixtures/              # From phenotype-org-audits
│   └── schemas/
└── tests/
    └── ...
```

## Phase Plan

### Phase 0 (this doc) — Inventory + plan
- [x] Inventory all 8 source repos
- [x] Document merge target
- [ ] Get user approval on Go-as-host decision (vs Python-as-host)

### Phase 1 — Read-only diff pass
- [ ] `diff cheap-llm-mcp cheap-llm-mcp-deprecate` — extract unique provider code
- [ ] `diff cheap-llm-mcp cheap-llm-mcp-t1-19` — extract unique
- [ ] `diff dispatch-mcp dispatch-mcp-t1-0` — extract unique
- [ ] `diff dispatch-mcp dispatch-mcp-t1-5` — extract unique
- [ ] `diff phenotype-ops-mcp phenotype-ops-mcp-t1-11..14` — extract unique
- [ ] Identify which provider CLI/HTTP surface is canonical (cheap_llm vs dispatch)

### Phase 2 — Build Go bridge
- [ ] `go mod init github.com/kooshapari/phenotype-ops-mcp` (if not done)
- [ ] Add `providers/cheap_llm/provider.go` calling cheap-llm-mcp via subprocess
- [ ] Add `tools/dispatch/dispatch.go` consuming `github.com/kooshapari/thegent-dispatch`
- [ ] Wire into main MCP server
- [ ] Add tests

### Phase 3 — Migrate consumers
- [ ] Update all `cheap-llm-mcp` consumers → `phenotype-ops-mcp/providers/cheap_llm`
- [ ] Update all `dispatch-mcp` consumers → `phenotype-ops-mcp/tools/dispatch`
- [ ] PR per consumer

### Phase 4 — Delete source repos
- [ ] Archive cheap-llm-mcp, cheap-llm-mcp-deprecate, cheap-llm-mcp-t1-19
- [ ] Archive dispatch-mcp, dispatch-mcp-t1-0..t1-5
- [ ] Archive phenotype-ops-mcp-t0, t1-11..t1-14
- [ ] Update SSOT

## Risk / Open Questions

1. **Go vs Python host**: `phenotype-ops-mcp` is Go, but `cheap-llm-mcp` and `dispatch-mcp` are Python. Options:
   - (A) Keep Go host + Python subprocess bridge (current plan)
   - (B) Make Python the host and consume Go from Python (CGO/reverse)
   - (C) Make a thin polyglot host via gRPC/HTTP

2. **`phenotype-org-audits` overlap**: This is a "data" repo, not an executable. Keep as data, import schemas only.

3. **AgilePlus `agileplus-mcp` concept**: Agent 05 noted AgilePlus has audit patterns. Those should stay in AgilePlus (domain logic), but the generic repo audit schema/emit logic can move to ops-mcp.

## Action Items (Immediate)

- [ ] Pick a Phase 1 leader (subagent or human)
- [ ] Schedule diff pass for cheap-llm-mcp variants
- [ ] Schedule diff pass for dispatch-mcp variants
- [ ] Schedule diff pass for phenotype-ops-mcp variants
- [ ] Decide Go-vs-Python host in ADR
- [ ] Build Go bridge after ADR
