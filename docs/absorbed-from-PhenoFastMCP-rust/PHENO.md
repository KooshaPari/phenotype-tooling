# PhenoFastMCP-rust

Phenotype **tier-0 Rust** MCP framework fork of
[Dicklesworthstone/fastmcp_rust](https://github.com/Dicklesworthstone/fastmcp_rust).

Explicit **Rust port of [fastmcp](https://github.com/PrefectHQ/fastmcp)** — high-level server
builder, `#[tool]` / `#[resource]` / `#[prompt]` macros, cancel-correct async (asupersync),
and a multi-crate workspace (`fastmcp-protocol`, `fastmcp-server`, `fastmcp-transport`, etc.).

This is the Rust sibling of PhenoFastMCP (Python) and PhenoFastMCP-go — **not** the official
low-level MCP SDK. For spec/compliance primitives use [PhenoRMCP](https://github.com/KooshaPari/PhenoRMCP).

## Upstream (GitHub fork — required)

| Field | Value |
|-------|-------|
| Parent | `Dicklesworthstone/fastmcp_rust` (`fork: true`) |
| Python sibling | [PhenoFastMCP](https://github.com/KooshaPari/PhenoFastMCP) ← PrefectHQ/fastmcp |
| Go sibling | [PhenoFastMCP-go](https://github.com/KooshaPari/PhenoFastMCP-go) ← mark3labs/mcp-go |
| Spec sibling | [PhenoRMCP](https://github.com/KooshaPari/PhenoRMCP) ← modelcontextprotocol/rust-sdk |
| Branches at fork | **2** |
| crates.io | `fastmcp-rust` (check upstream releases) |

**Do not** mirror into an empty repo — use:

```bash
gh repo fork Dicklesworthstone/fastmcp_rust --fork-name PhenoFastMCP-rust
```

### Sync

```bash
git remote add upstream https://github.com/Dicklesworthstone/fastmcp_rust.git
git fetch upstream --tags
git checkout main && git merge upstream/main && git push origin main
```

## Tradeoffs (read before embedding in substrate)

| Topic | Notes |
|-------|-------|
| Runtime | **asupersync** (cancel-correct), not tokio — bridge at server boundary |
| Toolchain | Rust 2024 edition, **nightly** required |
| Transports | stdio mature; SSE/WS at transport layer — HTTP server integration external |
| Upstream PRs | Author does not merge outside contributions; phenotype fork owns deltas |
| Maturity | Early (pre-1.0 API); smaller community than rmcp |

## Ergonomics cherry-pick sources (not primary forks)

| Repo | Role |
|------|------|
| [JSBtechnologies/FastRMCP](https://github.com/JSBtechnologies/FastRMCP) | tokio-native middleware/SSE patterns — evaluate for superset |
| [Epistates/turbomcp](https://github.com/Epistates/turbomcp) | enterprise MCP SDK — separate lane if needed |

## Role in Phenotype

See [LANGUAGE-TIERS-AND-ROLES.md](https://github.com/KooshaPari/PhenoMCPServers/blob/main/docs/LANGUAGE-TIERS-AND-ROLES.md).

- **Tier 0** MCP framework (`fastmcp_rust`) — fastmcp-equivalent Rust core
- **parallel_lane:** `phenofastmcp-rust` — parallel with Go/Python framework forks
- **Not** a generic `phenotype-rust-sdk` — domain is MCP framework only; other Rust → phenoUtils/substrate
- **Not** rmcp — use PhenoRMCP for official SDK / spec conformance

See `FORK-NOTES.md`.
