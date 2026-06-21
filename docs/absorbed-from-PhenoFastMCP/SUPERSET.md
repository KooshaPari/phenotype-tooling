# phenotype/superset — Wave 2B integration lane

**Baseline:** `v3.4.2` tag on [PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp)
(`feat/phenotype-foundation` docs: PHENO.md + FORK-NOTES.md)

**Purpose:** Long-lived branch for selective upstream merges and Phenotype-specific
patches before promoting to `main`. Canonical Python framework lane per ADR-017 (tier 2).

## Integration status (2026-06-17)

| Item | State |
|------|-------|
| GitHub fork parent | `PrefectHQ/fastmcp` (`fork: true`, 140 branches) |
| Baseline tag | `v3.4.2` |
| Upstream branches merged | **none yet** — branch tracks foundation docs only |
| Priority triage | see FORK-NOTES.md § Priority branches |
| Sibling lanes | [PhenoFastMCP-go](https://github.com/KooshaPari/PhenoFastMCP-go) PR #3, [PhenoFastMCP-rust](https://github.com/KooshaPari/PhenoFastMCP-rust) PR #2 merged |

## Upstream branch triage policy

The fork inherits **140 upstream heads**. Do **not** merge all branches wholesale.

1. **Baseline:** reset or rebase `phenotype/superset` from `v3.4.2` (or latest upstream release tag) monthly.
2. **Selective merges only:** cherry-pick or `--no-ff` merge candidate branches from the priority table in `FORK-NOTES.md` after smoke tests pass.
3. **Track decisions:** open GitHub issues labeled `superset-merge` for each accepted/rejected branch.
4. **Reject by default:** Claude/Codex one-off issue branches, dependabot bumps, and unreleased experiments unless fleet needs them.
5. **Promote to main:** only after pytest + MCPForge/ops-mcp smoke on this branch.

### Initial priority candidates (from FORK-NOTES.md)

| Branch | Why |
|--------|-----|
| `main` | baseline sync |
| `2-14-deprecations` | v2 migration path |
| `anthropic-sampling-handler` | provider sampling |
| `auto-docket-execution` | background task execution |
| `apps-quickstart-tutorial` | MCP Apps docs/samples |
| `add-jmespath-tools-contrib` | tool contrib patterns |
| `chat` | chat transport experiments |

Pull-request heads exist in the local mirror bare clone only (`refs/pull/*` cannot push to GitHub).

## Merge workflow

```bash
git fetch upstream --tags
git checkout -B phenotype/superset v3.4.2
git merge main   # keep phenotype foundation docs current
# for each triaged branch:
git merge --no-ff upstream/<branch> -m "superset: merge upstream/<branch>"
# run: uv run pytest && ops-mcp smoke
git push origin phenotype/superset
```

## Related

- ADR-017 polyrepo boundaries (PhenoFastMCP = tier 2 framework binding)
- PhenoMCPServers `catalog/registry.yaml` framework.python entry
- Spec SDK (`rmcp`) stays in **PhenoRMCP**, not here
