# Absorbed from dispatch-mcp — 2026-06-18

**Source:** `KooshaPari/dispatch-mcp` (deleted 2026-06-18)
**Target:** `KooshaPari/phenotype-tooling/docs/absorbed-from-dispatch-mcp/`

## What Was Here

dispatch-mcp was a Model Context Protocol (MCP) server acting as a headless worker dispatcher:
- `src/dispatch_mcp/` — MCP server entry point, request router
- `src/dispatch_mcp/providers/` — LLM provider adapters (llama_cpp, openai_compat)
- `src/dispatch_mcp/tiers/` — Cost/budget/quota/audit middleware
- `tests/` — Provider mock backend tests

## Prior Absorptions (already done before wave-3)

Per L5-104 migration plan, the W2-1 work was already absorbed:
- 6 cost/budget/quota/audit modules → `pheno-mcp-router` (PR #1)
- LlamaAdapter → `pheno-mcp-router` (PR #2)
- OpenAICompatAdapter → `pheno-mcp-router` (PR #3)
- llama-cpp docker setup → `phenotype-ops` (PR #2)
- Deprecation notice → `dispatch-mcp` consumer side (PR #1)

## Why Deleted

After L5-104 migration, only the orchestrator shell remained. Per ADR-008 (dispatch-mcp as sole MCP server, later superseded by ADR-037 pheno-mcp-router substrate), the orchestrator role is now `pheno-mcp-router` itself. Source repo has no further active development.

## License

MIT (inherited from dispatch-mcp)
