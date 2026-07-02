# WP-08 — Bench CI & Regression Guard

**Status**: ✅ Complete (committed `a7984181` WP-07, WP-08 to follow)
**Target**: nightly regression detection across all criterion benchmarks
**Owner**: tooling-bench
**Depends on**: WP-02 (criterion benches), WP-07 (CLI access to `pt <cmd>`)

---

## Goal

Run `cargo bench` on a nightly schedule across every workspace member that
declares `[[bench]]` in `Cargo.toml`. Detect regressions greater than a configured
threshold percentage (default `5%`) and publish a report artefact plus a
PR-comment for branch runs.

## Architecture

```
            ┌──────────────────────────┐
            │  .github/workflows/      │
            │  ci-bench.yml (nightly)  │
            └────────────┬─────────────┘
                         │ schedule / push
                         ▼
            ┌──────────────────────────┐
            │ cargo bench              │
            │   phenotype-diff         │
            │   temporal-grounding     │
            └────────────┬─────────────┘
                         │ *.txt (bencher format)
                         ▼
            ┌──────────────────────────┐
            │ scripts/                 │
            │   bench_parse_criterion  │
            │   bench_diff             │
            └────────────┬─────────────┘
                         │ report (md + txt + manifest.json)
                         ▼
   ┌─────────────────────────────────────────────┐
   │  compare current vs BENCHMARKS.md baseline │
   │  exit 0  → no regression                    │
   │  exit 1  → regression > threshold          │
   │  exit 2  → baseline missing / parse error  │
   └─────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|---|---|
| `scripts/bench_parse_criterion.py` | Parses criterion `--output-format bencher` text → JSON list of `{name, value, unit}` |
| `scripts/bench_diff.py` | Loads baseline `BENCHMARKS.md`, parses current artefacts, diffs p100 (or any centile), emits report + manifest |
| `BENCHMARKS.md` | Source of truth baseline — table form, parser-friendly |
| `.github/workflows/ci-bench.yml` | Nightly cron + push-triggered run + dispatch |

## Exit Code Contract

| Exit | Meaning |
|---|---|
| `0` | No regression > threshold, or only improvements / new benches |
| `1` | At least one existing benchmark regressed in `p100` (or whichever centile was used) by > threshold % |
| `2` | Fatal — baseline missing/ malformed, JSON parse error, missing artefact directory |
| `3` | New benchmarks added (not present in baseline) — informational |

Re-runs are idempotent: the report deterministic names mean no rotation drift.

## Threshold Tiers

| Tier | % | Action |
|---|---|---|
| Nominal | ≤ 5% | Pass; record observation |
| Warning | > 5%, ≤ 10% | Fail CI but allow `--threshold` override + `#bench-waive` PR label to acknowledge |
| Hard fail | > 10% | Fail CI, require explicit `#bench-revert` or fix-forward PR |

The default threshold is **5%** as adopted from the Phase 2 plan.

## Manifest Format (`manifest.json`)

```json
{
  "schema": "bench-manifest/v1",
  "generated_at": "2026-06-29T03:00:00Z",
  "commit": "a7984181",
  "baseline_source": "BENCHMARKS.md @ a7984181",
  "threshold_pct": 5.0,
  "results": [
    {
      "crate": "phenotype-diff",
      "bench": "diff_apply::case_large",
      "value": 1.23e-3,
      "unit": "s",
      "baseline": 1.20e-3,
      "delta_pct": 2.5,
      "status": "ok"
    }
  ],
  "summary": { "ok": 4, "warn": 0, "fail": 0, "new": 2, "removed": 0 }
}
```

## Adding a New Bench

1. Add a `benches/<name>.rs` to your crate.
2. Wire `[[bench]]` in your crate's `Cargo.toml`:
   ```toml
   [[bench]]
   name = "my_new_bench"
   harness = false
   ```
3. Open a PR. CI will run the bench, **add** it to the report as `new`, and exit 3 (informational) — exactly once. After merge, update `BENCHMARKS.md` to include the new row so subsequent runs diff against it.

## Acceptance Criteria

- [x] `cargo bench --workspace` succeeds on nightly schedule
- [x] `python scripts/bench_parse_criterion.py < artefact.txt` produces ≥1 entry per benchmark sample
- [x] `python scripts/bench_diff.py --current bench_artifacts --baseline BENCHMARKS.md --threshold 5` exits 0 on a fresh baseline (or 3 if new benches were added)
- [x] `pipx install` style of the python scripts requires only stdlib
- [x] CI workflow reads `BENCHMARKS.md` from the same commit being benched and uploads `bench_artifacts/`
- [x] `manifest.json` round-trips: regenerate, parse, compare

## Outstanding (deferred to WP-09+)

- [ ] Grafana / OTLP scrape for benchmark trends (cross-system correlation)
- [ ] `pt bench --diff` UX (delegates into `scripts/bench_diff.py`)
- [ ] Cross-PR benchmark comparison (compare head to merge-base rather than just commit)
