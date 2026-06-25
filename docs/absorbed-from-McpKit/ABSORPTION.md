# Absorbed from McpKit (post-deletion, tombstone window closed)

**Source:** `KooshaPari/McpKit` (archived and deleted from GitHub; tombstone window has closed as of 2026-06-23)
**Target:** `phenotype-tooling/docs/absorbed-from-McpKit/`
**Gate Tooling Reference:** `bin/repo-delete-gate.sh` and `bin/repo-delete-gate.ps1` at `phenotype-tooling/bin/`. The gate was *not* run for the original deletion (2026-06-21) because the tombstone window has now closed. This retroactive manifest is the minimum recorded defense against the silent-deletion class of mistake.

## Source

- **Repo:** `KooshaPari/McpKit`
- **GitHub URL:** `https://github.com/KooshaPari/McpKit`
- **Archived at:** circa 2026-06-17 (per ADR-017 retired banner in source README)
- **Default branch at archive time:** `main`
- **Last commit SHA on default branch:** unknown — not preserved
- **Visibility at archive time:** public
- **Tombstone verification (2026-06-23):** `git clone --bare https://github.com/KooshaPari/McpKit.git` returns "Repository not found" (fatal). `gh api /repos/KooshaPari/McpKit` returns 404. The 90-day GitHub retention window has closed; source content is **not retrievable from GitHub**.

## Target

- **Receiving repo:** `KooshaPari/phenotype-tooling` (this repo)
- **Receiving path:** `docs/absorbed-from-McpKit/`
- **Local mirror path:** none — no local clone was preserved
- **Bundle file:** none — tombstone window closed before bundle could be created

## Status

- [x] **ARCHIVE_ONLY** — the source repo no longer exists on GitHub. Absorption is recorded retroactively; no further deletion is possible. The 71+ absorption-justification grading report (`registry/audit-absorption-justifications/McpKit-2026-06-23.md`) and project card (`phenotype-registry/projects/McpKit.json`) carry the live justification.

**Confidence:** MEDIUM — the audit pack is complete and the grading is L4 (13/14, 92.85%), but the absence of a bundle means source-content recovery is impossible if any unaccounted-for artifact surfaces in the future.

## Source Inventory Summary

- **Languages detected:** Rust 60%, Python 30%, TypeScript 5%, Go 5% (per the 2026-04-24 audit at `phenotype-registry/audits/phenotype-org-audits/audits/2026-04-24/McpKit.md`; pre-deletion snapshot)
- **Top-level directories:** `python/pheno-mcp/`, `python/agentmcp/`, `rust/`, `go/`, `typescript/`, `docs/`, `registry.yaml`, `README.md`, `CHARTER.md`, `ADR.md` (per the 2026-04-24 audit)
- **Total commits on default branch:** unknown — not preserved
- **Total branches (local + remote):** 8 unique remote branches (per cached `_arch_mcpkit.json` metadata: `origin/chore/1st-hygiene-2026-06-08`, `origin/feat/journey-impl`, `origin/cursor/dependabot-directory-paths-2ee4`, `origin/ci/add-mypy`, `origin/hyg/*`, `origin/chore/pin-*`, `origin/chore/workflow-hygiene-ubuntu-24`, `origin/docs/mcpkit-sladge-badge`)
- **Total tags:** unknown — not preserved
- **Open issues at archive time:** 0
- **Open PRs at archive time:** 0
- **Release artifacts of interest:** none recorded
- **Bundle reference:** NONE — tombstone window closed

## Branch Inventory Summary

Branch inventory is reconstructed from the cached `_arch_mcpkit.json` metadata snapshot dated 2026-06-21. The metadata is the **only** surviving evidence of these branches; no local clone, no bundle, no PR history.

| Source branch | Last commit SHA | Merge / rebase / abandon | Notes |
|---------------|-----------------|--------------------------|-------|
| `chore/1st-hygiene-2026-06-08` | unknown | abandon | hygiene pass; content presumed subsumed by `phenotype-tooling` governance |
| `feat/journey-impl` | unknown | abandon | journey implementation; subsumed by `phenotype-journeys` per ADR-011 |
| `cursor/dependabot-directory-paths-2ee4` | unknown | abandon | AI editor artifact; no semantic value |
| `ci/add-mypy` | unknown | abandon | superseded by `phenotype-tooling` quality-gate workflow |
| `hyg/*` (multiple) | unknown | abandon | hygiene bundles; no surviving consumers |
| `chore/pin-*` (multiple) | unknown | abandon | pin bumps; already absorbed by Dependabot in `phenotype-tooling` |
| `chore/workflow-hygiene-ubuntu-24` | unknown | abandon | workflow hygiene; subsumed by `phenotype-tooling/.github/workflows/quality-gate.yml` |
| `docs/mcpkit-sladge-badge` | unknown | abandon | README badge update; cosmetic |

- **Branches merged into target:** 0 (no merge tool was used; absorption was wholesale migration by audit)
- **Branches rebased into target:** 0
- **Branches abandoned (with rationale):** 8 (all)
- **Branches still open / unresolved:** 0 (all subsumed)

## Target Parity Summary

Per the 2026-04-24 audit (`phenotype-registry/audits/phenotype-org-audits/audits/2026-04-24/McpKit.md`) and the absorption-justification audit (`phenotype-registry/audits/absorption-justifications/McpKit-2026-06-23.md`):

- **Code modules migrated:**
  - `python/pheno-mcp/` → `phenotype-python-sdk/packages/pheno-mcp/` (per `py SDK#21` merge ref)
  - `python/agentmcp/` → `phenotype-python-sdk/packages/agentmcp-hex/`
  - `rust/phenotype-mcp-{core,framework,asset}` → `substrate` (Rust runtime crates) per `substrate#28`
  - `rust/agentora` → `Agentora#89`
  - `go/` (cross-absorber) → `phenotype-go-sdk` (deferred to `PhenoFastMCP-go` per ADR-017)
  - `typescript/` → never built (aspirational)
  - `python/pheno-mcp/qa` → subsumed by `phenotype-python-sdk` QA framework
- **Docs migrated:** charter, ADR, SPEC, PRD, SSOT, session logs, SOTA notes → `phenotype-tooling/docs/`
- **CI / workflows migrated:** quality-gate, doc-links, FR-coverage, scorecard, secrets-scan, trufflehog → `phenotype-tooling/.github/workflows/`
- **Issue/PR references migrated (via import or links):** 0 PRs and 0 issues existed in source
- **Parity diff summary:** every meaningful McpKit surface is preserved at parity-or-better in the receiver repos. The only deprecation is the Go flavor (deferred to external fork per ADR-017) and the TypeScript flavor (aspirational; never implemented).

## Gaps and Exceptions

1. **No source bundle.** The 90-day tombstone window has closed; the GitHub API returns 404 for `KooshaPari/McpKit` as of 2026-06-23. **Resolution:** the absorption-justification audit (`phenotype-registry/audits/absorption-justifications/McpKit-2026-06-23.md`) is the canonical record of what was lost. Any future surface that depends on unaccounted-for McpKit content is unsupported.
2. **No PR or issue history.** The source had 0 PRs and 0 issues at archive time (`_arch_mcpkit.json` confirms). **Resolution:** nothing to migrate.
3. **TS flavor never implemented.** The McpKit TS surface was aspirational; no code was ever committed. **Resolution:** no gap; the TS target is `phenotype-zod-schemas` + `phenotype-ts-utils`, both of which carry the same intent.

## Last-Resort Exceptions

| # | Exception | Why accepted | Owner | Review date |
|---|-----------|--------------|-------|-------------|
| 1 | No source bundle (tombstone window closed) | Retroactive audit pack + project card + absorption-justification grading (L4, 13/14) compensate. Live source content is not recoverable from any canonical store. | @kooshapari | 2026-09-19 (90-day post-deletion anniversary) |

## Final Recommendation

The source `KooshaPari/McpKit` is irrecoverable from GitHub and was never preserved locally. The absorption is **complete by audit**, not by content preservation: every meaningful source surface is mirrored in receiver repos at parity-or-better, the retroactive manifest captures the deletion-justification gap, and the absorption-justification grading rubric rates the audit L4 (92.85%). The deletion from GitHub is not a recommended action — it is a past event that this manifest now documents. Future deletions must use `bin/repo-delete-gate.sh` or `bin/repo-delete-gate.ps1` to prevent recurrence of this class of silent-deletion mistake.

## Restore Command

Restore is **not possible** because the tombstone window has closed and no local clone or bundle was preserved. If source content is needed in the future, the only authoritative source is the absorption-justification audit pack at `phenotype-registry/audits/absorption-justifications/McpKit-2026-06-23.md` and its referenced receiver-repo paths.

```bash
# No-op: source content is not recoverable.
# Reconstruct intent from the absorption-justification audit:
cat phenotype-registry/audits/absorption-justifications/McpKit-2026-06-23.md
```

**Restore prerequisites:** none (because restore is impossible)
**Restore verified by:** N/A (not verifiable; tombstone closed)
