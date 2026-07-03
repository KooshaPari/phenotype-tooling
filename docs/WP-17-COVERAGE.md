# WP-17: Coverage + Mutation Harness

**Status:** Implemented
**Branch:** `feat/wp17-coverage`
**Depends on:** WP-14 (branch protection + PTX gate as required check)

## Goal

Close the correctness gap that benches + clippy can't catch:
- **Line/branch coverage** via `cargo-llvm-cov`, enforced at 80% threshold
- **Mutation testing** via `cargo-mutants`, weekly schedule with per-crate matrix
- Coverage + mutation scores flow into the same gate that protects `main`

## Workflows

| File | Purpose |
|---|---|
| `.github/workflows/coverage.yml` | PR-time `cargo-llvm-cov --workspace --all-features --lcov`. Fails if total line coverage drops below 80%. Uploads `lcov.info` + `coverage-html/` artifacts. On main, also commits a coverage badge to `.badges/coverage.svg`. |
| `.github/workflows/mutation.yml` | Weekly Monday 04:00 UTC + on-demand. Per-crate matrix (29 crates, 4 excluded as no-logic forwarders). Uses `cargo mutants` with `--timeout 60 --jobs 2`. Fails if any mutant survives (no test catches the mutation). |

## Thresholds

Defined in `coverage.toml`:

| Metric | Threshold | Where enforced |
|---|---|---|
| Line coverage (workspace) | ≥ 80% | `coverage.yml` job summary + `awk` exit |
| Branch coverage (workspace) | ≥ 70% | advisory (not enforced yet) |
| Critical-crate coverage | ≥ 90% | advisory (not enforced yet) |

**Critical crates** (paths where correctness regressions are most costly):
- `phenotype-cli` — user-facing dispatcher
- `phenotype-config` — runtime configuration schema
- `phenotype-diff` — diff/merge correctness
- `phenotype-tooling-observability` — SLO tracking
- `ptx` — gate runner

## Excluded paths

`coverage.toml` lists path globs excluded from coverage measurement. Tests/benches/examples are excluded by convention (they exercise other code, not themselves).

## Why nightly mutation instead of PR-time?

Mutation testing is **expensive**. A single PR on a 22-crate workspace with default cargo-mutants timeouts would run for hours. The matrix approach (one job per crate, parallel) keeps each job bounded, but the total CI minutes per run are still high. Hence:

- **PR-time:** `cargo-llvm-cov` only (fast, ~3-5 min for the workspace)
- **Nightly:** `cargo-mutants` per-crate matrix (each crate ~10-60 min, parallel across the matrix)

When a mutant survives a nightly run, the failing artifact (`mutants-<crate>`) gets uploaded and the next morning's triage picks up the offending crate.

## Critical-crate coverage bootstrap

Current coverage of the 5 critical crates is unknown. Once WP-17's `coverage.yml` runs end-to-end, the badge will land at whatever the real percentage is. If below 80%:

1. Bump `line_coverage_min` only after the gap is closed (don't lower the threshold to make CI green)
2. Open one issue per critical crate below 90% titled "test: bring `<crate>` to 90% coverage"
3. Each issue scoped to a single crate's uncovered lines (lcov.info + `cargo llvm-cov report --html`)

## Adoption criteria for new crates

When adding a new crate to the workspace:

1. Add it to the `mutation.yml` matrix
2. Run `cargo llvm-cov` locally to verify it doesn't drag the workspace average below 80%
3. If the crate is a critical-crate candidate, propose its inclusion in `coverage.toml::thresholds.critical_crates` in a follow-up PR
4. The acceptance gate for the new crate is `cargo test --workspace` passing + coverage threshold met

## Tooling

- **cargo-llvm-cov** ≥ 0.6.0 (installed via `cargo install cargo-llvm-cov --locked`)
- **cargo-mutants** ≥ 24.x (installed via `cargo install cargo-mutants --locked`)
- **llvm-tools-preview** Rust component (for `llvm-cov` / `llvm-profdata`)
- **RUSTFLAGS="-C instrument-coverage"** drives LLVM source-based coverage

## Verification (this commit)

- `coverage.yml` validates YAML syntax (GitHub-side on first run)
- `mutation.yml` matrix has 29 crates with 4 excluded
- `coverage.toml` parses as JSON
- `docs/WP-17-COVERAGE.md` documents rollout + acceptance criteria

End-to-end CI validation happens on first push to a PR branch — both workflows will run automatically.