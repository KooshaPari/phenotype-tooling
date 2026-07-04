# WP-23 — Coverage as Required Branch-Protection Check

**Phase:** 5 (WP-23)
**Status:** Implemented, ready for branch-protection rollout
**Author:** Forge
**Date:** 2026-07-04

## What this WP closes

Phase 4's `coverage.yml` workflow (`cargo llvm-cov` with `--fail-under-lines 80 --fail-under-branches 75`) ran on every PR + push to main, but its conclusions were **advisory** — a PR with 50% line coverage could still merge if reviewers didn't notice the workflow failed.

WP-23 makes coverage a **required** branch-protection check. After this WP:

1. `cargo test -p foo --no-run` will exit non-zero if any member crate drops below the threshold
2. `coverage.yml` runs on every PR and push, and its conclusion blocks merge
3. Coverage delta vs main is posted as a PR comment automatically
4. Bypassing coverage requires admin override (logged in `#governance-bypass`)

## Acceptance criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | `.github/workflows/coverage.yml` is listed as required check on `main` | `gh api repos/KooshaPari/phenotype-tooling/branches/main/protection/required_status_checks` returns `coverage` in `contexts[]` |
| 2 | PR with deliberate coverage regression fails to merge | Open a PR that deletes `#[cfg(test)] mod tests {...}` in one crate; merge button is greyed out |
| 3 | Coverage delta vs main posted on every PR | PR shows comment `coverage-delta: lines -3.2%` from `forge-ci[bot]` |
| 4 | Admin override produces audit entry | `gh api repos/KooshaPari/phenotype-tooling/branches/main/protection/required_status_checks/.../dismissals` shows the bypass with actor + reason |

## Configuration

### Branch protection (`.github/branch-protection/main.json`)

Added to `required_status_checks.contexts[]`:

```json
"coverage",
"mutation-score"
```

(The existing `ptx / governance` check from WP-14 remains in the list.)

### Coverage thresholds (`.coverage.toml`)

```toml
[coverage.run]
source = ["crates"]

[coverage.report]
fail_under_lines = 80
fail_under_branches = 75
fail_under_functions = 70
exclude_lines = [
  "unsafe {",
  "debug_assert!",
  "#\\[cfg\\(test\\)\\]",
]
```

### Workflow (`.github/workflows/coverage.yml`)

Already in place from WP-17. WP-23 adds:

1. **`--fail-under-lines 80`** to `cargo llvm-cov` invocation
2. **PR comment** step using `dgageot/comment-pull-request@v2` with coverage delta
3. **`exit 1`** on threshold violation (already present)
4. **Matrix per crate** so per-crate coverage is independently tracked (crates can fail individually without blocking the whole workspace)

## Per-crate matrix

The coverage workflow runs against each member crate independently:

```yaml
strategy:
  matrix:
    crate:
      - acceptance-contract
      - agent-forecast
      - agent-orchestrator
      - anthropic-usage-poll
      - audit-privacy
      - bench-guard
      - commit-msg-check
      - dag-scheduler
      - doc-link-check
      - docs-health
      - fr-coverage
      - fr-trace
      - legacy-scan
      - phenotype-cli
      - phenotype-config
      - phenotype-diff
      - phenotype-tooling-observability
      - ptx
      - quality-gate
      - release-cut
      - sbom-gen
      - temporal-grounding
      - worktree-manager
```

This means a coverage regression in `quality-gate` doesn't block `fr-trace`. Each crate's coverage gate is its own row in the required-check matrix.

## Coverage delta PR comment

The PR-comment job uses `dgageot/comment-pull-request@v2` with a templated body:

```markdown
## Coverage report

| Crate | Lines Δ | Branches Δ | Functions Δ |
|-------|---------|------------|-------------|
| `phenotype-cli` | -3.2% | -1.1% | -2.8% |
| `quality-gate` | +0.5% | +0.2% | +0.1% |
| `release-cut` | ±0.0% | ±0.0% | ±0.0% |

**Total**: lines -2.7% / branches -0.9% / functions -2.5%

> Crates below the 80% line threshold are highlighted in red above and
> must be brought back above 80% before this PR can merge.
```

## Bypass procedure

When a PR legitimately needs to merge with low coverage (new crate with no tests, prototype phase), the reviewer with admin access can:

1. Go to the PR's failed check
2. Click "Re-run jobs" → "Re-run failed jobs" does NOT bypass
3. Instead: click "Dismiss" → enter reason (`"new crate, tests planned in follow-up"`) → this creates an audit entry in `#governance-bypass`
4. PR can then merge

The audit log is queryable via:

```bash
gh api repos/KooshaPari/phenotype-tooling/branches/main/protection/required_status_checks/contexts/coverage
```

## Migration

The rollout is staged to avoid surprise blockages:

1. **Day 0**: WP-23 code lands; `coverage` is added to `required_status_checks` but with `strict: false` (existing checks still pass even if coverage fails)
2. **Day 7**: Set `strict: true` for `coverage` — now coverage failures genuinely block merge
3. **Day 14**: Set `enforcement_level: non_admins` so only admins can dismiss
4. **Day 30**: Tighten per-crate thresholds to 85% lines / 80% branches (was 80/75)

The Phase 5 plan calls for day-0 → day-7 transition in the same sprint as the WP-23 rollout.

## Related

- WP-17: Coverage + mutation harness (parent)
- WP-14: Branch protection + `ptx` as required check (sibling)
- WP-24: Mutation-score gate (companion, both wired as required checks together)
- `docs/WP-17-COVERAGE.md` — the original coverage WP