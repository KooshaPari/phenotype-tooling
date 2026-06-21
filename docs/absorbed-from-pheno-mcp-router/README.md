# pheno-mcp-router

Generic MCP router that wraps a single backend HTTP endpoint (like OmniRoute) with tier allowlisting, payload sanitization, response allowlisting, and structured logging.

It replaces per-MCP-server boilerplate. `dispatch-mcp` would consume this and shrink to ~80 lines.

## Install

```bash
pip install pheno-mcp-router
```

## What It Provides

- FastMCP server wiring
- Tier allowlisting
- Tool registration per tier
- Payload key allowlisting
- Request size limits
- Response size limits
- Response field allowlisting
- Structured logs for dispatch attempts and failures
- A small scaffold command for new MCP wrappers

## Example

```python
from pheno_mcp_router import McpRouter

router = McpRouter(
    name="dispatch-minimax",
    backend_url="http://localhost:20128/v1/chat/completions",
)
router.add_tier("default", {"model": "minimax/minimax-m1"})
router.serve()
```

## dispatch-minimax As 3 Lines

```python
from pheno_mcp_router import McpRouter
router = McpRouter("dispatch-minimax", "http://localhost:20128/v1/chat/completions").add_tier("default", {"model": "minimax/minimax-m1"})
router.serve()
```

## CLI

```bash
pheno-mcp-router init dispatch-minimax
```

This creates a small MCP server package that imports `McpRouter`, configures one backend endpoint, adds tiers, and starts FastMCP.

## Security Model

The router is defensive by default:

- Only explicitly allowed payload keys are forwarded.
- Oversized requests are rejected before backend dispatch.
- Oversized responses are rejected before returning to MCP clients.
- Only allowlisted response keys are returned.
- Backend route configuration is tier scoped.

## Development

```bash
hatch run pytest
hatch run pheno-mcp-router --help
```
