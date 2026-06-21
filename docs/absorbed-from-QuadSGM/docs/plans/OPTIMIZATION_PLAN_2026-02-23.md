# 4sgm Optimization Plan — 2026-02-23

## Current State (after Phase 1 fixes)
- Python: ~11.4K source LOC (20.7K total w/ tests)
- 0 ruff violations (fixed)
- tach.toml added (module boundaries)
- server.py split into 8 domain tool modules (1,615 → 125 LOC)
- tools_upgraded.py deleted (903 LOC dead code removed)

## Remaining Optimization Tracks

### Track 1: Spec System (documentation)
- Flesh out PRD.md with user stories and acceptance criteria
- Flesh out FUNCTIONAL_REQUIREMENTS.md with FR SHALL statements + FR IDs
- Add PLAN.md with phased WBS
- Link tests to FR IDs via pytest marks

### Track 2: Type Safety
- Update pyrightconfig to strict mode (currently basic)
- Add pyright to pre-commit config
- Fix type errors surfaced by strict mode
- Remove backend/pyproject.toml (consolidate into root pyproject.toml)

### Track 3: Test Coverage
- Add coverage reporting: pytest --cov with fail_under=90
- Add coverage badge to README.md
- Identify uncovered paths in MCP tools after server.py refactor

### Track 4: MCP Server Quality
- Verify all 26 tools work after server.py split (run pytest mcp_server/tests/)
- Add domain tests for new tools/ modules (products, inventory, pricing, etc.)
- Wire mcp_server to backend repositories (currently uses in-memory only)

### Track 5: Frontend Quality
- Run next lint + tsc --noEmit
- Ensure vitest + playwright pass
- Consolidate Tailwind config if duplicated

## Architecture Outcome
- MCP server: domain-split modules ✅ (done)
- Backend: repository protocol pattern ✅ (already good)
- Agents: LangGraph StateGraph ✅ (already good)
- Tests: 36 files, good coverage structure ✅
- Boundaries: tach.toml added ✅
- Strict types: TODO
- Spec traceability: TODO
