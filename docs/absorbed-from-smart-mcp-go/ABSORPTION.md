# Absorbed from smart-mcp-go (post-deletion, NO_MERIT_WITH_INTENT)

**Source:** `KooshaPari/smart-mcp-go` (archived and deleted from GitHub; local clone removed 2026-06-23)
**Target:** `phenotype-tooling/docs/absorbed-from-smart-mcp-go/`
**Gate Tooling Reference:** `bin/repo-delete-gate.sh` and `bin/repo-delete-gate.ps1` at `phenotype-tooling/bin/`. The gate was *not* run for the original deletion because no manifest existed at the time; the local clone was removed in the Phase 0 closeout (F2, 2026-06-23). This retroactive manifest closes the gap and ensures the gate is the default path for any future deletion.

## Source

- **Repo:** `KooshaPari/smart-mcp-go`
- **GitHub URL:** `https://github.com/KooshaPari/smart-mcp-go`
- **Archived at:** unknown (pre-2026-06-17)
- **Default branch at archive time:** `main`
- **Last commit SHA on default branch:** unknown — not preserved
- **Visibility at archive time:** unknown
- **Tombstone verification (2026-06-23):** `gh api /repos/KooshaPari/smart-mcp-go` returns 404. The 90-day retention window has closed (or the repo was never in active retention); no tombstone available.

## Target

- **Receiving repo:** `KooshaPari/phenotype-tooling` (this repo)
- **Receiving path:** `docs/absorbed-from-smart-mcp-go/`
- **Local mirror path:** `C:\Users\koosh\Dev\smart-mcp-go` (empty placeholder; **removed 2026-06-23** as part of Phase 0 F2 closeout)
- **Bundle file:** none — no source content to bundle

## Status

- [x] **ARCHIVE_ONLY** — the source repo no longer exists on GitHub. Absorption is **NO_MERIT_WITH_INTENT**: the repo had no source content, no CI, no tests, and no public API. The 71+ absorption-justification grading report (`phenotype-registry/audits/absorption-justifications/smart-mcp-go-2026-06-23.md`) and project card (`phenotype-registry/projects/smart-mcp-go.json`) carry the live justification.

**Confidence:** HIGH — every claim in this manifest is verifiable from the 2026-06-23 ground-truth inspection (the local dir was 0 files / 0 bytes; the remote returns 404).

## Source Inventory Summary

- **Languages detected:** none — local clone was 0 files; remote `languages_url` returns 404
- **Top-level directories:** none — local clone was empty
- **Total commits on default branch:** unknown — not preserved
- **Total branches (local + remote):** unknown
- **Total tags:** unknown
- **Open issues at archive time:** unknown
- **Open PRs at archive time:** unknown
- **Release artifacts of interest:** none
- **Bundle reference:** NONE — no source content to bundle

## Branch Inventory Summary

Branch inventory is **empty**. The local clone had no working tree (verified by `dir` returning 0 files at `C:\Users\koosh\Dev\smart-mcp-go` on 2026-06-23). The remote returns 404, so no remote-branch data is retrievable. The repo name pattern suggests an aspirational "Go MCP SDK" intent that was never implemented.

| Source branch | Last commit SHA | Merge / rebase / abandon | Notes |
|---------------|-----------------|--------------------------|-------|
| *(none)*      | n/a             | n/a                      | No branches preserved; no source content to enumerate |

- **Branches merged into target:** 0
- **Branches rebased into target:** 0
- **Branches abandoned (with rationale):** 0
- **Branches still open / unresolved:** 0

## Target Parity Summary

There is **no target parity to demonstrate** because there was no source content to absorb. The aspirational "Go MCP SDK" intent is now owned by `phenotype-go-sdk` and the deferred `PhenoFastMCP-go` fork (per ADR-017). If a Go MCP SDK ever ships, it will be in those repos, not in a resurrection of `smart-mcp-go`.

- **Code modules migrated:** none
- **Docs migrated:** none
- **CI / workflows migrated:** none
- **Issue/PR references migrated (via import or links):** none
- **Parity diff summary:** no diff; the source had no content

## Gaps and Exceptions

1. **No source content.** The local clone was 0 files; the remote is 404. **Resolution:** the aspiration for a Go MCP SDK is owned by `phenotype-go-sdk` and `PhenoFastMCP-go`. No source content to recover.
2. **No intent doc preserved.** The repo name implies a "smart MCP Go SDK" but no README, no charter, no ADR was committed. **Resolution:** the canonical intent doc is `phenotype-go-sdk/intent.md` and `phenotype-go-sdk/ADR-017.md`, both of which cover the actual Go MCP scope.

## Last-Resort Exceptions

| # | Exception | Why accepted | Owner | Review date |
|---|-----------|--------------|-------|-------------|
| 1 | No source content to recover | The repo had no source content at the time of removal. The aspiration is owned by `phenotype-go-sdk` and `PhenoFastMCP-go`; any future Go MCP work will land there. | @kooshapari | 2026-09-19 |

## Final Recommendation

The source `KooshaPari/smart-mcp-go` had **no source content of any kind** at the time of removal. Absorption is complete by the absence of content: the local clone (0 files) was removed on 2026-06-23 as part of Phase 0 F2 closeout, and the remote is 404. The aspirational intent is now owned by `phenotype-go-sdk` and `PhenoFastMCP-go`. The deletion from GitHub is not a recommended action — it is a past event that this manifest now documents for traceability. Future deletions must use `bin/repo-delete-gate.sh` or `bin/repo-delete-gate.ps1` to ensure the manifest is in place **before** the deletion, not after.

## Restore Command

Restore is **not possible** because no source content ever existed locally, the remote is 404, and the tombstone window has closed. If a Go MCP SDK is needed in the future, the canonical home is `phenotype-go-sdk` (or `PhenoFastMCP-go` per ADR-017).

```bash
# No-op: source content never existed; the aspiration is owned elsewhere.
# Use the canonical Go MCP home:
gh repo clone KooshaPari/phenotype-go-sdk
# or, per ADR-017:
gh repo clone KooshaPari/PhenoFastMCP-go
```

**Restore prerequisites:** GitHub access to `KooshaPari/phenotype-go-sdk` (or `KooshaPari/PhenoFastMCP-go`)
**Restore verified by:** N/A (no original content to verify; canonical Go MCP home is the authoritative replacement)
