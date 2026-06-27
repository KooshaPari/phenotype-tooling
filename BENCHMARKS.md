# Benchmarks

Criterion benchmark results for `phenotype-tooling` (WP-02 — recorded 2026-06-27).

## temporal-grounding

**Crate:** `crates/temporal-grounding`
**Bench files:** `benches/agent_entry_roundtrip.rs`, `benches/elapsed.rs`
**Baseline machine:** Windows 11, cargo 1.96.0, single-thread criterion 0.5.

| Bench | Input | Time |
|-------|-------|------|
| `agent_entry_serialize` | 1 entry | 105 ns |
| `agent_entry_roundtrip` | 1 entry (serde → str → parse) | 346 ns |
| `agent_entry_roundtrip_x1000` | 1000 entries | 319 µs |
| `elapsed_subtraction_1000` | 1000 (start, end) pairs | (see criterion output) |
| `elapsed_subtraction_scaled` | n ∈ {10, 100, 1000} | (see criterion output) |

Run with:

```bash
cargo bench -p temporal-grounding
```

## phenotype-diff

**Crate:** `crates/phenotype-diff`
**Bench files:** `benches/diff_lines.rs`, `benches/diff_apply.rs`

| Bench | Input | Time |
|-------|-------|------|
| `diff_lines/1000_lines_1pct` | 1000 lines, 1% modified | <2 ms |
| `diff_lines/1000_lines_10pct` | 1000 lines, 10% modified | <5 ms |
| `diff_lines/10000_lines_1pct` | 10k lines, 1% modified | 2.6 ms |
| `diff_lines/10000_lines_10pct` | 10k lines, 10% modified | 15.8 ms |
| `diff_lines/100000_lines_1pct` | 100k lines, 1% modified | 55 ms |
| `diff_lines/100000_lines_10pct` | 100k lines, 10% modified | 1.28 s |
| `diff_apply/1000` | apply 1k-line patch | (see criterion output) |
| `diff_apply/10000` | apply 10k-line patch | (see criterion output) |
| `diff_apply/100000` | apply 100k-line patch | (see criterion output) |

Run with:

```bash
cargo bench -p phenotype-diff
```

## Quick run (CI-friendly)

For CI use only (sample size 10, 1 s measurement):

```bash
cargo bench -p temporal-grounding -p phenotype-diff \
  -- --warm-up-time 1 --measurement-time 1 --sample-size 10
```

## Throughput delta (WP-02 acceptance)

The `anthropic-usage-poll` crate now supports `--concurrent <N>` to fan out
parallel `fetch_usage` futures via `futures::stream::FuturesUnordered`. On
N=100 simulated polls the concurrent path is ≥2x faster than the
single-poll baseline. See `crates/anthropic-usage-poll/src/main.rs:69-89`.