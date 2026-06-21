# AGENTS.md — pheno-mcp-router

## Purpose

Generic FastMCP router that wraps a single backend HTTP endpoint (e.g.
OmniRoute, OpenAI, Anthropic) with tier allowlisting, payload
sanitization, response allowlisting, and structured logging. Replaces
per-MCP-server boilerplate.

## Build & Test

```bash
just dev        # pip install -e ".[dev]"
just test       # pytest -v
```

## Repo conventions

- Uses FastMCP (not the official `mcp` package) for the simpler decorator API
- `McpRouter` is a dataclass; configure with chained `.add_tier().add_tool()` calls
- `httpx.AsyncClient` for backend HTTP; `asyncio` is required for `.serve()`
- Tier allowlist is the **primary security control** — never bypass

## Public API

```python
from pheno_mcp_router import McpRouter

router = McpRouter(
    name="dispatch-minimax",
    backend_url="http://localhost:20128/v1/chat/completions",
    sanitize_keys={"model", "messages", "temperature", "max_tokens"},
    response_keys={"id", "model", "choices", "usage"},
    max_message_bytes=128_000,
    max_response_bytes=512_000,
)
router.add_tier("minimax", {"model": "minimax-m2p7"})
router.add_tool("minimax", my_local_tool)
router.serve()
```

## Do Not Touch

- The default `sanitize_keys` / `response_keys` — these are the **security
  contract** for every MCP server that uses this router. Bumping them
  requires a security review.
- The `add_tier` / `add_tool` ordering — tiers must be added before tools
  that reference them (`add_tool` raises `ValueError("unknown tier")`).

## Reference

- See `/Users/kooshapari/CodeProjects/Phenotype/repos/FLEET_100TASK_DAG_V4.md`
  §63.1 (V10 L10 Security) and §78.6 (V13 grand-total).
- See `dispatch-mcp` and `cheap-llm-mcp` for the existing 2 consumers.
