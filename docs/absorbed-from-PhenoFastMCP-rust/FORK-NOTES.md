# Fork notes — PhenoFastMCP-rust

Last updated: 2026-06-17

## Why fastmcp_rust (not rmcp)

| Repo | Role |
|------|------|
| **Dicklesworthstone/fastmcp_rust** (this fork) | FastMCP-equivalent: macros, server builder, batteries-included DX |
| [modelcontextprotocol/rust-sdk](https://github.com/modelcontextprotocol/rust-sdk) | Official low-level SDK (`rmcp`) — see **PhenoRMCP** fork |
| JSBtechnologies/FastRMCP | tokio fastmcp clone — cherry-pick only (tiny community) |

Phenotype standardizes on **fastmcp_rust** for the PhenoFastMCP-rust name and tier-0 framework
boundary. rmcp was incorrectly forked here initially (2026-06-17); repo was deleted and re-forked.

## Create (canonical)

```bash
gh repo delete KooshaPari/PhenoFastMCP-rust --yes   # only when re-parenting
gh repo fork Dicklesworthstone/fastmcp_rust --fork-name PhenoFastMCP-rust
```

Verified: `fork: true`, `parent: Dicklesworthstone/fastmcp_rust`, **2 branches**, **8 tags**.

## Spec / compliance fork (sibling)

```bash
gh repo fork modelcontextprotocol/rust-sdk --fork-name PhenoRMCP
```

Use PhenoRMCP when you need official `rmcp` transports, streamable HTTP, OAuth, or spec tests —
not for PhenoFastMCP branding.

## Superset candidates

Track merges into `phenotype/superset` (create from latest upstream tag):

| Source | Notes |
|--------|-------|
| `main` | baseline |
| FastRMCP middleware/SSE | cherry-pick patterns only |
| FastRMCP middleware/SSE | **closed** — eval [docs/eval/Fastrmcp.md](docs/eval/Fastrmcp.md); no picks |
| PhenoRMCP rmcp releases | optional interop layer, not merge wholesale |

## Related

- Python: KooshaPari/PhenoFastMCP
- Go: KooshaPari/PhenoFastMCP-go
- Spec SDK: KooshaPari/PhenoRMCP
- Servers: KooshaPari/PhenoMCPServers
