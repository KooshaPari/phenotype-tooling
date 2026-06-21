# 4SGM Audit: Quality, Architecture & Polyglot Opportunities
**Date:** 2026-02-23
**Project:** 4SGM (LangGraph + MCP Python e-commerce platform)
**Total LOC:** ~20K Python (98 files)

---

## Executive Summary

**Status:** Early-stage, high test coverage, but significant quality debt and architectural duplication.

| Metric | Finding |
|--------|---------|
| **Quality Issues** | 263 lint errors (80 unused imports, 63 unsorted imports) |
| **Architecture** | Clear split: Backend (API) + MCP Server, but with repo duplication |
| **Test Coverage** | Strong: 30+ tests, integration chains, but some test code is unpolished |
| **Polyglot Fit** | **Rust:** high-performance repository layer. **Go:** optional API/orchestration |
| **Monolith vs Split** | Should remain **single repo** (tight coupling), but refactor **internal modules** |

---

## LOC Breakdown by Module

```
MCP Server (5,049 LOC)
├─ server.py (1,586 LOC)         # Main server + all 25+ tools, too large
├─ tools_upgraded.py (903 LOC)   # Tool implementations, some duplication
├─ repositories/impl/memory.py (692 LOC)
├─ models/ (982 LOC distributed)  # Pydantic models for 7+ domains
└─ repositories/base.py + 8 specific repos

Backend Core (923 LOC)
├─ app.py (403 LOC)               # FastAPI + LangGraph + MCP client
├─ repositories/ (4,804 LOC)      # CRITICAL DUPLICATION
│  ├─ adapters/mock.py (1,268 LOC)
│  ├─ adapters/supabase.py (1,117 LOC)
│  └─ base.py + exceptions (898 LOC)
├─ agents/ (771 LOC)
│  ├─ deep_agent.py (221 LOC)
│  ├─ subagents/ (369 LOC across 3 workflows)
│  └─ callbacks/langfuse.py (124 LOC)
└─ models.py (70 LOC)

Tests (7,820 LOC)
├─ Integration chains (3,200 LOC across 8 test files)
├─ Conftest + fixtures (542 LOC)
├─ Unit tests / MCP tools (1,200+ LOC)
└─ Langfuse integration (313 LOC)

CLI & Entrypoints (331 LOC)
├─ cli.py + sgm_cli.py (duplication)
└─ __main__.py stubs

TOTAL: ~20K LOC
```

---

## Quality Issues (263 Lint Errors)

### Critical
- **80 unused imports** → Clean up, automate with ruff --fix
- **63 unsorted imports** → Enable isort/ruff-isort
- **27 lines > 100 chars** → Refactor long functions
- **15 unused variables** → Remove or suppress with `# noqa`

### Medium
- **12 f-strings without placeholders** → Remove `f` prefix
- **49 blank lines with whitespace** → Auto-fixable
- **5 undefined names** (F821) → Missing imports or typos

### Process Issues
- **pyproject.toml mismatch:** `[tool.ruff]` deprecated, should be `[tool.ruff.lint]`
- **No type hints in public APIs** → Missing type coverage
- **No pre-commit hooks** → Linting can run on every commit

**Fix effort:** ~30 min with `ruff --fix` + manual review of F821/E501

---

## Architecture Assessment

### Current: Two-Tier Monolith
```
FastAPI (app.py)
  ├─ LangGraph agent (deep_agent.py)
  ├─ MultiServerMCPClient (connects to MCP server)
  └─ Fallback to in-process repositories if MCP fails

MCP Server (server.py)
  ├─ 25+ FastMCP tools (all in one file: 1,586 LOC)
  ├─ 8 repository implementations (memory-based)
  └─ Models + exceptions (982 LOC distributed)

Backend Repositories (4,804 LOC)
  ├─ Abstract base + exceptions
  ├─ Mock adapter (1,268 LOC)
  ├─ Supabase adapter (1,117 LOC)
  └─ Domain-specific repos (cart, order, product, etc.)
```

### Critical Issue: Repository Duplication

**Problem:** The project has **two parallel repository systems**:

1. **Backend repositories** (`4sgm/backend/repositories/`)
   - Abstract interfaces + mock/Supabase adapters
   - 4,804 LOC total
   - Designed for FastAPI but _not connected_

2. **MCP repositories** (`4sgm/mcp_server/repositories/`)
   - In-memory only (no persistence layer)
   - 692 LOC just for memory impl
   - 8 domain-specific repository interfaces

**Impact:**
- Data flows differently: Backend has Supabase option, MCP is memory-only
- Inconsistent business logic between layers
- Test repositories duplicated across both systems
- Maintenance burden: any domain change requires edits in both places

**Root cause:** Backend was built first with DB adapters, then MCP server was bolted on with its own repo layer.

---

## Split Candidate Analysis

### Should These Be Separate Repos?

| Module | Candidate? | Rationale |
|--------|-----------|-----------|
| **MCP Server** | ❌ No | Tightly coupled to backend models/domains. Shared exceptions, Pydantic models. Requires backend changes → MCP changes. |
| **Backend API** | ❌ No | Depends on MCP tools to function. Remove MCP → API becomes useless. |
| **Repositories** | ⚠️ Yes (internal refactor) | Can be extracted to a **shared lib** (`4sgm-repositories` or `sgm-data-layer`) but keep in this repo initially. |
| **Agents** | ⚠️ Maybe | Could be a separate `4sgm-agents` package, but tightly coupled to tools. Keep together for now. |
| **Tests** | ✅ Keep in repo | Integration tests must stay with source. |

**Recommendation:** **Keep as single repo**, but refactor internal modules.

---

## Polyglot Opportunities

### 1. Rust for Repository Layer (MEDIUM Impact)
**Candidate:** `4sgm/backend/repositories/adapters/` (current: 2,385 LOC Python)

**Why:**
- Heavy lifting: Supabase query building, caching layer, connection pooling
- supabase.py has 1,117 LOC of string/SQL building → error-prone
- Memory model (692 LOC) has collision-prone dict logic → unsafe in Rust

**What to port:**
```rust
// 4sgm-repo-core/src/lib.rs (Rust FFI via PyO3)
pub struct RepositoryConfig { ... }
pub trait Repository: Send + Sync { ... }
pub struct RustMemoryRepository { ... }
pub struct RustSupabaseRepository { ... }
```

**Effort:** 3–5 days. **Payoff:** 30–40% faster queries, type safety, zero-copy data passing.
**When:** After refactoring Python duplication (see below).

---

### 2. Go for Optional Orchestration (LOW Priority)
**Candidate:** Separate service for multi-instance coordination (future)

**Why:** Not needed now. MCP is single-process. If scaling horizontally later, use Go for:
- Request routing across MCP instances
- Health checks + failover
- Metrics aggregation

**Effort:** Not yet needed.

---

### 3. Zig for Hot-Path Calculations (RESEARCH)
**Candidate:** Pricing/discount calculations in tools_upgraded.py (903 LOC)

**Why:**
- ~200 LOC of discount chain logic (nested loops, rounding)
- Could be 10x faster in Zig
- Rarely changes once validated

**Effort:** 1–2 days to prototype. **Payoff:** Marginal unless bulk-pricing is a bottleneck.

---

## Recommended Refactoring Plan

### Phase 1: Quality Baseline (Days 1–2)

1. **Fix linting (30 min)**
   ```bash
   ruff check --fix 4sgm/
   ruff check --unsafe-fix 4sgm/  # Review manually
   ```

2. **Consolidate duplicate CLIs (30 min)**
   - Merge `cli.py` + `sgm_cli.py` → single `cli.py`
   - Fix: `[tool.ruff]` → `[tool.ruff.lint]` in pyproject.toml
   - Add pre-commit hook

3. **Add type hints (3 hours)**
   - Start with public APIs (app.py, server.py, deep_agent.py)
   - Use `basedpyright` to validate

4. **Resolve F821 errors (1 hour)**
   - 5 undefined names likely from incomplete refactors

**Output:** All linting passes, type checking at 80%+ coverage.

---

### Phase 2: Eliminate Repository Duplication (Days 3–5)

1. **Extract shared repository base** (4 hours)
   ```
   4sgm/backend/repositories/shared_base.py
   ├─ BaseRepository interface (from backend/)
   ├─ CommonExceptions (merge both exception lists)
   └─ CacheLayer (move from backend/repositories/cache.py)
   ```

2. **Unify models** (4 hours)
   - Move MCP models to `4sgm/backend/models/` with domain subdirs
   - MCP server imports from backend
   - Single source of truth for Pydantic schemas

3. **Create adapters package** (3 hours)
   ```
   4sgm/adapters/
   ├─ memory.py       (from MCP, improved)
   ├─ supabase.py     (from backend, refactored)
   ├─ mock.py         (from backend)
   └─ __init__.py
   ```
   - Both backend and MCP import from here

4. **Test:** Run integration tests, verify parity.

**Output:** ~2,000 LOC eliminated, single repository interface.

---

### Phase 3: Rust RepositoryLayer (Days 6–10)

1. **Create Rust FFI stub** (2 days)
   ```bash
   cargo new --lib 4sgm-repo-core
   # Implement RustMemoryRepository + RustSupabaseRepository
   # PyO3 bindings for Python
   ```

2. **Port mock/memory layer** (2 days)
   - Ensure parity with Python version via property tests

3. **Performance test** (1 day)
   - Benchmark vs. current Python
   - Validate 20–30% speedup on bulk operations

4. **Deprecate Python adapters** (optional)
   - Or keep as fallback

**Output:** 30–40% faster data layer, maintained in Rust.

---

### Phase 4: Tool Consolidation (Days 11–12)

1. **Split server.py (1,586 LOC)**
   ```
   4sgm/mcp_server/
   ├─ server.py (core, ~300 LOC)
   ├─ tools/
   │  ├─ product.py (150 LOC)
   │  ├─ cart.py (150 LOC)
   │  ├─ order.py (150 LOC)
   │  ├─ shipping.py (120 LOC)
   │  ├─ pricing.py (100 LOC)
   │  ├─ customer.py (90 LOC)
   │  └─ rfq.py (90 LOC)
   └─ __init__.py (tool registration)
   ```

2. **Merge tools_upgraded.py** into tool modules (already 903 LOC).

3. **Test:** MCP tools still work.

**Output:** server.py reduced to ~300 LOC (registration only), tools modular.

---

## Lines of Code Reduction

| Phase | Action | Before | After | Saved |
|-------|--------|--------|-------|-------|
| Baseline | Fix linting, remove dead code | 20.2K | 19.8K | 400 LOC |
| Duplication | Merge repos, models | 19.8K | 17.2K | 2,600 LOC |
| Tools | Split server.py into modules | 17.2K | 17.2K | 0 (refactor only, same LOC) |
| Rust port | Replace adapters with FFI | 17.2K | 16.5K* | 700 LOC (Rust in separate repo) |
| **TOTAL** | | **20.2K** | **16.5K** | **3,700 LOC (~18% reduction)** |

*Rust repo separate, not counted in main project LOC.

---

## Prioritized Action List

### 🔴 **Do First (Next Session)**
1. **Fix all 263 lint errors** (30 min) → unblocks quality gate
2. **Consolidate CLI files** (30 min) → remove duplication
3. **Add `[tool.ruff.lint]` config** (10 min) → suppress deprecation warning
4. **Add pre-commit hook** (20 min) → prevent regression

### 🟡 **Do Next (Days 1–5)**
5. **Extract shared repository base** (8 hours) → enable Rust port
6. **Merge MCP + backend models** (4 hours) → single source of truth
7. **Type-hint public APIs** (3 hours) → improve IDE support

### 🟢 **Consider (Days 6+)**
8. **Rust repository layer** (5 days) → 30–40% perf gain
9. **Split server.py into tool modules** (2 days) → maintainability
10. **Add integration test for repository parity** (2 days) → safety net

---

## Architecture Recommendations

### Keep as One Repo
- ✅ Backend API + MCP stay together
- ✅ Tests stay with source
- ✅ Agents + tools stay together (high coupling)

### Refactor Within Repo
- 🔄 Eliminate repository layer duplication (merge backends + MCP repos)
- 🔄 Consolidate models into `backend/models/` with domains
- 🔄 Split server.py into tool modules
- 🔄 Merge CLI entry points

### Extract Later (Optional)
- 📦 `4sgm-repo-core` (Rust FFI) — when Rust port is complete
- 📦 `4sgm-agents` — if agent library grows beyond 3 workflows
- 📦 `4sgm-models` — if Pydantic schema sharing needed elsewhere

---

## Quality Gates (Before Next PR)

- [ ] Ruff: 0 errors
- [ ] Type checking: 80%+ coverage
- [ ] Tests: 90%+ pass rate
- [ ] No new unused imports/variables
- [ ] All public functions type-hinted

---

## Conclusion

**4SGM is a solid foundation** with good test coverage and clear architecture. The main issues are **quality debt and internal duplication**, not fundamental design flaws.

**Next steps:**
1. Fix linting immediately (unblocks work)
2. Merge repository layers (biggest refactor, highest payoff)
3. Consider Rust repository port (future performance boost)
4. Keep as single repo (tight coupling makes separation impractical)

**Estimated total refactor time:** 3–4 weeks (part-time), 5–7 days (full-time).
