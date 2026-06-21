# Status

Last updated: 2026-06-08

## Build
GitHub Actions billing-blocked org-wide. Workflows are configured but not running.

## Quality gates
- markdown lint: local (via CI when billing restored)
- link checks: local
- governance file presence: enforced

## Current state
- Branch: `main` (default) — **SSOT is `docs/reference/{prd,adr,requirements}.md` and `docs/guide/`**
- Working tree: clean
- Stashes: 0
- Open PRs: 0
- Open issues: 0 (4 welcome spam closed in D8)

## Recent changes
- D7: removed `Taskfile.yml` (cargo-only recipes were wrong for docs-only repo; `justfile` is the SSOT)
- D7: dropped stale `stash@{0}` (WIP on `docs/productization` was redundant with the hygiene merge)
- D7: deleted 8 stale local branches
- D8: closed 4 welcome-spam issues (#25, #26, #27, #28)
- D8: reconciled two phenoXdd lineages — `main` is the canonical SSOT (workflow hygiene + `docs/reference/` governance)
- T0 (2026-06-08): governance audit on branch `chore/t0-docs-audit-2026-06-08`; no runtime artefacts added. See `T0-AUDIT-2026-06-08.md` for the full 14-axis score.

## Cross-references
See `phenotype-org-governance/SUPERSEDED.md` for canonical authority.

---

## T0 audit (2026-06-08)

14-axis governance score, mirrored from `T0-AUDIT-2026-06-08.md`:

| #   | Axis                            | Status |
|-----|---------------------------------|--------|
| 1   | Charter & SSOT                  | green  |
| 2   | README / substantive content    | green  |
| 3   | CONTRIBUTING                    | green  |
| 4   | SECURITY                        | green  |
| 5   | LICENSE                         | green  |
| 6   | CHANGELOG                       | yellow |
| 7   | CI workflows                    | yellow |
| 8   | Test / verification methodology | green  |
| 9   | Secret scanning                 | green  |
| 10  | Governance bodies               | green  |
| 11  | Local quality gates             | green  |
| 12  | Editor / hygiene                | green  |
| 13  | Cross-references to org hub     | yellow |
| 14  | Commit hygiene & status         | yellow |

**Score**: 11 green · 3 yellow · 0 red → **89%**.

Drift items recorded in `T0-AUDIT-2026-06-08.md:6` (CLAUDE.md misleading
`pip install` line, AGENTS.md non-UTF-8 corruption, `docs/reference/index.md`
referencing non-existent root files). None fixed in T0; all deferred to
follow-up PRs.
