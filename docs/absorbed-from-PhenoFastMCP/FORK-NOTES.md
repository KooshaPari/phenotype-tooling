# Fork notes — PhenoFastMCP superset strategy

Last updated: 2026-06-17 (re-forked as proper GitHub fork)

## REQUIRED: GitHub fork relationship

`KooshaPari/PhenoFastMCP` **must** remain `fork: true` with parent
`PrefectHQ/fastmcp`. This enables:

- GitHub "Sync fork" / compare against upstream
- Fork network visibility and contribution path upstream
- Accurate `parent` / `source` in API and Dependabot

**Never** bootstrap by creating an empty repo and `git push --mirror` — that
produces `fork: false` and cannot be converted later without delete + re-fork.

### Create (canonical)

```bash
gh repo fork PrefectHQ/fastmcp --fork-name PhenoFastMCP
# omit --default-branch-only so all upstream branches copy into the fork network
```

Verified: `fork: true`, `parent: PrefectHQ/fastmcp`, **140 branches**.

### Daily upstream sync (working clone)

```bash
git remote add upstream https://github.com/PrefectHQ/fastmcp.git   # once
git fetch upstream --tags
git checkout main && git merge upstream/main
git push origin main
```

## Supplemental mirror push (branches only — after fork exists)

Use only to backfill branches if upstream adds new heads before you sync.
GitHub **rejects** `refs/pull/*` on push.

```bash
# 1. Mirror clone upstream (includes all heads, tags, and pull refs locally)
git clone --mirror https://github.com/PrefectHQ/fastmcp.git fastmcp.git
cd fastmcp.git

# 2. Point at phenotype fork and disable mirror push mode
git remote set-url origin https://github.com/KooshaPari/PhenoFastMCP.git
git config remote.origin.mirror false

# 3. Push all branches and tags (NOT pull refs)
git push origin 'refs/heads/*:refs/heads/*'
git push origin 'refs/tags/*:refs/tags/*'
```

Verified after proper re-fork: **140 branches** on `KooshaPari/PhenoFastMCP`.

Pull-request heads are preserved **locally** in the mirror bare repo at
`fastmcp.git` for cherry-pick / merge review. They cannot live on GitHub as refs.
Export list:

```bash
git for-each-ref --format='%(refname)' refs/pull/ | wc -l
```

## Upstream remote (working clone)

```bash
git remote add upstream https://github.com/PrefectHQ/fastmcp.git
git fetch upstream --tags
git fetch upstream '+refs/heads/*:refs/remotes/upstream/*'
```

## Superset merge policy

Goal: collect useful upstream branches into `phenotype/superset` so day-0
phenotype users inherit fixes/features without waiting for upstream releases.

### Priority branches (initial triage)

| Branch | Why |
|--------|-----|
| `main` | baseline |
| `2-14-deprecations` | migration path from v2 |
| `anthropic-sampling-handler` | provider sampling |
| `auto-docket-execution` | background task execution |
| `apps-quickstart-tutorial` | MCP Apps docs/samples |
| `add-jmespath-tools-contrib` | tool contrib patterns |
| `chat` | chat transport experiments |

### Merge workflow

```bash
git checkout -B phenotype/superset v3.4.2
# for each candidate branch:
git merge --no-ff upstream/<branch> -m "superset: merge upstream/<branch>"
# run tests; if green, keep; else document conflict in issue
```

Track every merge decision in GitHub issues labeled `superset-merge`.

## Related forks (framework tier-0, separate repos)

| Language | Upstream candidate | Phenotype repo | Status |
|----------|-------------------|----------------|--------|
| Python | PrefectHQ/fastmcp | **this repo** | GitHub fork (140 branches) |
| Go | mark3labs/mcp-go | [PhenoFastMCP-go](https://github.com/KooshaPari/PhenoFastMCP-go) | GitHub fork (53 branches) |
| Rust framework | Dicklesworthstone/fastmcp_rust | [PhenoFastMCP-rust](https://github.com/KooshaPari/PhenoFastMCP-rust) | GitHub fork (2 branches) |
| Rust spec SDK | modelcontextprotocol/rust-sdk | [PhenoRMCP](https://github.com/KooshaPari/PhenoRMCP) | GitHub fork |

Each tier-0 fork uses `gh repo fork` (never mirror-to-empty). See sibling `PHENO.md` files.

## Issues to file upstream (carry-over)

When phenotype patches fix bugs found during superset merges, open PRs against
`PrefectHQ/fastmcp` **and** keep phenotype commits on `feat/phenotype-*` until
upstream merges.

## Absorption from deprecated phenotype repos

| Source | Target | Notes |
|--------|--------|-------|
| McpKit framework crates | `rust/`, `go/` subtrees | drop vendored mcp-forge LSP copy |
| AgentMCP hex adapters | `python/pheno/` layer | use HexaKit templates for layout |
| PhenoMCP hand-rolled server | **delete** | use fastmcp APIs |
| phenotype-python-sdk mcp-kit | remove package | depend on PhenoFastMCP wheel |

Server **implementations** → [PhenoMCPServers](https://github.com/KooshaPari/PhenoMCPServers).
