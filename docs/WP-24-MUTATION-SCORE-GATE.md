# WP-24 — Mutation-Score Gate (Required Branch-Protection Check)

## Purpose

Promote the mutation-score check from advisory (WP-17) to **required**
(WP-24). Paired with WP-23, this means every PR must pass:

- `coverage` (lines ≥ 80%, branches ≥ 75%)
- `mutation-score` (aggregate caught-pct ≥ 60%)

before it can merge into `main`.

## Threshold

| Metric | Threshold | Source |
|---|---|---|
| `aggregate_caught_pct` | **≥ 60.00%** | `crates/phenotype-tooling-observability` mutation job |
| Per-crate caught-pct | no per-crate threshold | workspace-wide aggregate is the gate |
| Survivors | **must be zero** | unchanged from WP-17 (any surviving mutant fails the build) |

The 60% threshold matches the Phase 4 plan (`2026-07-02-PHASE4_BUILD_PLAN.md`)
default for WP-17. Raise to 70% once stable for 3 consecutive months.

## Architecture

```
PR opened against main
    │
    ├─► mutation.yml (matrix: each crate)
    │       └─► cargo mutants --output-format json
    │               └─► writes mutants-summary.txt per crate
    │                       └─► uploads as artifact
    │
    └─► mutation.yml (summarize job)
            ├─► downloads all mutants-summary.txt artifacts
            ├─► aggregates caught / missed / timeout / unviable
            ├─► computes aggregate_caught_pct = caught / (caught + missed)
            ├─► if aggregate_caught_pct < 60% → exit 1 (build fails)
            └─► posts PR comment with the score breakdown
```

The `mutation-score` job name surfaces in the PR check list so
branch-protection can require it.

## Triggers

- `pull_request` — every PR against `main` runs the full matrix + gate
- `schedule` (weekly cron) — same matrix but no PR comment, just artifact upload
- `workflow_dispatch` — manual trigger for hot-fix verification

Per-PR runs are the enforcement surface. The weekly cron is the
"did anything regress?" detector that runs when there's no PR activity.

## Acceptance criteria

- [x] `mutation.yml` has a `pull_request` trigger (not just cron)
- [x] `summarize` job computes `aggregate_caught_pct`
- [x] Build fails when `aggregate_caught_pct < 60%`
- [x] PR comment shows score breakdown per crate
- [x] Job name in PR check list is `mutation-score`
- [x] `branch-protection/main.json` requires `mutation-score` (WP-23)

## Rollout plan

| Phase | Duration | Behavior |
|---|---|---|
| Shadow (now) | 1 week | `mutation-score` check is wired but `continue-on-error: true` in summarize — failures don't block |
| Soft enforcement (week 2) | 1 week | Remove `continue-on-error`. Failures show as red check on PR but don't block merge |
| Hard enforcement (week 3+) | ongoing | `mutation-score` is a required check in `branch-protection/main.json` |

Each phase transition requires a code change in `mutation.yml`. The
`mutation-score` check name stays consistent so branch-protection
doesn't need to be re-wired mid-rollout.

## Override path

For emergency fixes (production-down scenarios), the on-call CODEOWNER
can override the check with a `mutation-override: &lt;reason&gt;` label on
the PR. The `summarize` job reads the label and skips the threshold
gate (still surfaces survivors as warnings). Override usage is logged
to a monthly review issue.

## Cost

- ~25 crates × ~5 min/run mutation testing = 2-3 hours wall-clock per
  PR run
- Acceptable for a release-grade workspace; can be reduced by
  excluding crates below a coverage threshold (excluded crates also
  excluded from mutation gating)

## Relationship to other WPs

| WP | Relationship |
|---|---|
| WP-17 | Set up the mutation job + workspace, advisory only |
| WP-23 | Promotes `coverage` and `mutation-score` to required checks |
| WP-24 (this) | Implements the threshold gate that WP-23 requires |

WP-17 + WP-23 + WP-24 close the "correctness gate" loop end-to-end:
crates are measured for coverage + mutation, and the results block
merges when below threshold.