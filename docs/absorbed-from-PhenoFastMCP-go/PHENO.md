# PhenoFastMCP-go

Phenotype **tier-0 Go** MCP framework fork of [mark3labs/mcp-go](https://github.com/mark3labs/mcp-go).

Chosen as the Go surface **closest to [fastmcp](https://github.com/PrefectHQ/fastmcp)**:
high-level server API, minimal boilerplate, stdio + Streamable HTTP + SSE transports.
Already used in the Phenotype fleet (e.g. MCPForge).

## Upstream (GitHub fork — required)

| Field | Value |
|-------|-------|
| Parent | `mark3labs/mcp-go` (`fork: true`) |
| Python sibling | [PhenoFastMCP](https://github.com/KooshaPari/PhenoFastMCP) ← PrefectHQ/fastmcp |
| Rust sibling | [PhenoFastMCP-rust](https://github.com/KooshaPari/PhenoFastMCP-rust) ← Dicklesworthstone/fastmcp_rust |
| Branches at fork | **53** |
| Spec alternative | [modelcontextprotocol/go-sdk](https://github.com/modelcontextprotocol/go-sdk) (official, stdio-focused) |

**Do not** mirror into an empty repo — use `gh repo fork mark3labs/mcp-go --fork-name PhenoFastMCP-go`.

### Sync

```bash
git remote add upstream https://github.com/mark3labs/mcp-go.git
git fetch upstream
git checkout main && git merge upstream/main && git push origin main
```

## Role in Phenotype

See [LANGUAGE-TIERS-AND-ROLES.md](https://github.com/KooshaPari/PhenoMCPServers/blob/main/docs/LANGUAGE-TIERS-AND-ROLES.md).

- **Tier 1** MCP framework (Go edge — justified for HTTP/SSE native servers)
- **parallel_lane:** `phenofastmcp-go` — develop in parallel with Rust/Python forks
- **Not** fleet runtime core (that stays Rust/substrate tier 0)

See `FORK-NOTES.md` for superset merge policy.
