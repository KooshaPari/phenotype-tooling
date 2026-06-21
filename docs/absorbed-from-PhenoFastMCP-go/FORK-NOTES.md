# Fork notes — PhenoFastMCP-go

Last updated: 2026-06-17

## Why mark3labs/mcp-go (not official go-sdk alone)

| SDK | Role |
|-----|------|
| **mark3labs/mcp-go** (this fork) | FastMCP-like DX: `NewMCPServer`, tool registration, HTTP/SSE/stdio |
| modelcontextprotocol/go-sdk | Official spec reference; thinner, stdio-first |

Phenotype standardizes on **mcp-go** for Go servers that mirror Python fastmcp ergonomics.
Use official go-sdk when spec-only compliance is required without HTTP transports.

## Create (canonical)

```bash
gh repo fork mark3labs/mcp-go --fork-name PhenoFastMCP-go
```

Verified: `fork: true`, `parent: mark3labs/mcp-go`, **53 branches**.

## Superset candidates

Track merges into `phenotype/superset` (create from latest release tag):

| Branch | Notes |
|--------|-------|
| `main` | baseline |
| (triage open PR branches via local `refs/pull/*` in mirror clone) | cherry-pick useful fixes |

## Related

- Python: KooshaPari/PhenoFastMCP
- Rust: KooshaPari/PhenoFastMCP-rust (fastmcp_rust), KooshaPari/PhenoRMCP (rmcp)
- Servers: KooshaPari/PhenoMCPServers
