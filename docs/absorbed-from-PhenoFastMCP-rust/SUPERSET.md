# phenotype/superset — Wave 2B integration lane

**Baseline:** `feat/phenotype-foundation` (PHENO.md + FORK-NOTES.md)

**Purpose:** Integration branch for fastmcp_rust upstream merges and selective FastRMCP
middleware evaluation. Official rmcp spec work belongs in **PhenoRMCP**, not here.

## Triage checklist

1. Track `Dicklesworthstone/fastmcp_rust` releases; merge tags here first.
2. Evaluate FastRMCP middleware/SSE patterns as cherry-picks only (issue #8 side-DAG).
3. asupersync/tokio bridge notes live in ADR appendix when picked.
4. Fork parent must remain `Dicklesworthstone/fastmcp_rust` — never rmcp.

2. ~~Evaluate FastRMCP middleware/SSE patterns as cherry-picks only (issue #8 side-DAG).~~ **Closed 2026-06-17** — see [docs/eval/Fastrmcp.md](docs/eval/Fastrmcp.md); empty cherry-pick queue; Axum HTTP integration deferred.
3. asupersync/tokio bridge notes live in ADR appendix when picked.
4. Fork parent must remain `Dicklesworthstone/fastmcp_rust` — never rmcp.

## FastRMCP evaluation addendum (2026-06-17)

Side-DAG `sd-fastrmcp-01`–`05` completed. **Recommendation: CLOSE** evaluation.

- Parent `fastmcp_rust` already covers middleware (short-circuit, caching, rate limits) and MCP-standard SSE framing.
- FastRMCP (2★, last push 2025-11-30) uses tokio/Axum with non-standard SSE `connectionId` events — high port cost, no net capability gain.
- Re-open only if FastRMCP gains sustained activity or upstream documents asupersync↔tokio bridge.

Full audit: [docs/eval/Fastrmcp.md](docs/eval/Fastrmcp.md).

## Related

- PhenoRMCP for `modelcontextprotocol/rust-sdk`
- PhenoMCPServers registry `framework.rust` + `framework.rmcp`
