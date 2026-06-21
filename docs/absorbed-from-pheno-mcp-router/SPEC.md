# pheno-mcp-router — SPEC

## Scope

Generic FastMCP router wrapping a backend HTTP endpoint (e.g. OmniRoute,
OpenAI, Anthropic) with tier allowlisting, payload sanitization, response
allowlisting, and structured logging. Replaces per-MCP-server boilerplate.

Implements V4 §63.1 (V10 L10 Security) + §78.6 (V13 grand-total) of
`FLEET_100TASK_DAG_V4.md`.

## Public API

- `class McpRouter` — FastMCP wrapper with chained fluent config:
  - `name: str`, `backend_url: str`
  - `sanitize_keys: set[str]` (default: model, messages, temperature, max_tokens)
  - `response_keys: set[str]` (default: id, model, choices, usage)
  - `max_message_bytes: int = 128_000`, `max_response_bytes: int = 512_000`
  - `timeout_seconds: float = 60.0`
  - `.add_tier(name, route) -> McpRouter`
  - `.add_tool(tier, fn) -> McpRouter`
  - `.dispatch(tier, payload) -> dict` (async)
  - `.serve() -> None`
- `class TierRoute` — `(name, route)` frozen dataclass.
- `LlmPort`, `LlmAdapter` — hexagonal L4 port + base adapter class.
- `OpenAIAdapter`, `AnthropicAdapter` — concrete LLM adapters.
- `StoragePort`, `StorageAdapter` — storage port + base adapter.
- `InMemoryStorageAdapter`, `JsonFileStorageAdapter` — concrete storage adapters.
- `ToolPort`, `ToolAdapter` — tool port + base adapter.

## Conventions

- **When to use:** building any new MCP server that wraps an LLM backend.
- **When NOT to use:** direct stdio MCP servers that do not proxy an HTTP backend.
- **5-line quickstart:**
  ```python
  from pheno_mcp_router import McpRouter
  r = McpRouter(name="my-mcp", backend_url="http://localhost:20128/v1/chat/completions")
  r.add_tier("default", {"model": "minimax-m2p7"}).serve()
  ```

## Configuration

All tunable defaults are centralized in ``src/pheno_mcp_router/config.py``.
Every module that previously defined hardcoded magic numbers now imports
from this single source of truth.

**Security-sensitive values** (``sanitize_keys``, ``response_keys``) are
NOT overridable at runtime — they are the contract between the router
and every MCP server it proxies.  See AGENTS.md §"Do Not Touch".

**Env-var overridable values** (read once at import time):

| Variable | Default | Description |
|---|---|---|
| ``PHENO_TIMEOUT_SECONDS`` | 60.0 | HTTP client timeout for all backends |
| ``PHENO_MAX_MESSAGE_BYTES`` | 128_000 | Max request payload before dispatch |
| ``PHENO_MAX_RESPONSE_BYTES`` | 512_000 | Max response payload from backend |

**LLM provider defaults** (``OPENAI_API_KEY``, ``ANTHROPIC_API_KEY``) are
read from the environment by the respective adapter at call time.

See ``.env.example`` for a reference template.

## Security model

- **Tier allowlist** (must `add_tier` first) — never bypass.
- **Payload sanitize_keys** — strip everything not in the allowlist.
- **Response allowlist** — strip everything not in the allowlist.
- **max_message_bytes / max_response_bytes** — prevent DoS.
- **structured logging** — every dispatch logs router, tier, bytes.

## Quality bar

- 71-pillar score: 24/71 (Tier 0)
- Test matrix: 3+ smoke tests in `tests/`
- Coverage: pending measurement
- License: dual (MIT + Apache-2.0)

## See also

- ADR-023 (Rule 3.1 substrate quality bar)
- ADR-013 (pheno-mcp-router canonical substrate)
- V4 §78.6 (V13 grand-total, MCP router substrate)