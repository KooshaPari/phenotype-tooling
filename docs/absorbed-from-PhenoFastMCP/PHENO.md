# PhenoFastMCP

Phenotype-org hard fork of [PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp).

This repository is the **MCP framework boundary** — server/client SDK, transports,
tool registration, and CLI. It is **not** a collection of deployable MCP servers;
those live in [PhenoMCPServers](https://github.com/KooshaPari/PhenoMCPServers).

## Upstream (GitHub fork — required)

This repo **must** be a GitHub fork so upstream tracking works in the UI and API.

| Field | Value |
|-------|-------|
| Parent | [PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp) (`fork: true`) |
| Baseline tag | `v3.4.2` |
| Sync remote | `upstream` → `https://github.com/PrefectHQ/fastmcp.git` |
| Branches at fork | **140** (GitHub copies all heads when not using default-only) |
| Tags | inherited via fork network / fetch upstream |

**Do not** recreate by mirror-pushing into an empty repo — that breaks the fork link.

Create (once):

```bash
gh repo fork PrefectHQ/fastmcp --fork-name PhenoFastMCP
```

Sync ongoing:

```bash
git fetch upstream
git merge upstream/main   # or rebase phenotype branches
```

## Phenotype extensions (planned)

See fleet normative doc:
[PhenoMCPServers — Language tiers and roles](https://github.com/KooshaPari/PhenoMCPServers/blob/main/docs/LANGUAGE-TIERS-AND-ROLES.md)

**This repo = tier 2 MCP framework binding** (fastmcp). Protocol core lives in
[PhenoFastMCP-rust](https://github.com/KooshaPari/PhenoFastMCP-rust) (tier 0).
Go edge framework: [PhenoFastMCP-go](https://github.com/KooshaPari/PhenoFastMCP-go) (tier 1, justified).

Work **in parallel** with sibling forks (`parallel_lane: phenofastmcp-py`).

Python (fastmcp) remains the primary binding today. **Tier-0 sibling forks** (separate repos, each with `fork: true`):

| Language | Repo | Upstream parent | Why (fastmcp analogue) |
|----------|------|-----------------|------------------------|
| Python | **this repo** | PrefectHQ/fastmcp | fastmcp |
| Go | [PhenoFastMCP-go](https://github.com/KooshaPari/PhenoFastMCP-go) | mark3labs/mcp-go | high-level server API + HTTP/SSE (MCPForge) |
| Rust | [PhenoFastMCP-rust](https://github.com/KooshaPari/PhenoFastMCP-rust) | Dicklesworthstone/fastmcp_rust | fastmcp-equivalent framework (tier 0) |
| Rust spec | [PhenoRMCP](https://github.com/KooshaPari/PhenoRMCP) | modelcontextprotocol/rust-sdk | official `rmcp` SDK |

Tier-1 bindings (C#, TS, Java) generate from these tier-0 forks.

## Consumption

```bash
pip install git+https://github.com/KooshaPari/PhenoFastMCP.git@v3.4.2
# or editable during dev:
pip install -e ".[dev]"
```

Deployable servers depend on this package; they do **not** vendor framework code.

## Governance

- `main` tracks upstream `main` plus phenotype merge commits
- `feat/phenotype-foundation` — docs, fork policy, first phenotype patches
- `phenotype/superset` — integration branch for merged useful upstream branches

See `SUPERSET.md` for integration-lane status and upstream triage policy.
See `FORK-NOTES.md` for branch merge inventory and sync commands.
