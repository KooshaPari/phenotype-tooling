# phenotype/superset — Wave 2B integration lane

**Baseline:** `feat/phenotype-foundation` (PHENO.md + FORK-NOTES.md + catalog cross-links)

**Purpose:** Long-lived branch for cherry-picking upstream fixes and Phenotype-specific
patches before merging to `main`. Mirrors Python `PhenoFastMCP` `phenotype/superset` workflow.

## Triage checklist

1. Merge latest upstream release tag into this branch (monthly).
2. Cherry-pick fleet-needed PRs from upstream (HTTP/SSE parity, transport fixes).
3. Run MCPForge / ops-mcp smoke against this branch before tagging Phenotype release.
4. Do **not** merge rmcp wholesale — spec SDK stays in PhenoRMCP.

## Related

- ADR-017 polyrepo boundaries
- PhenoMCPServers `catalog/registry.yaml` framework.go entry
