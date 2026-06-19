# Absorbed from Metron — 2026-06-18

**Source:** `KooshaPari/Metron` (deleted 2026-06-18)
**Target:** `KooshaPari/phenotype-tooling/docs/absorbed-from-metron/`

## What Was Here

Metron was a Rust crate for Prometheus-style metrics:
- `src/metrics.rs` — Counter, Gauge, Histogram primitives
- `src/registry.rs` — Metric registry
- `src/exporter.rs` — Prometheus text format exporter
- 3 unmerged commits preserved here:
  - `b4fa6f7` — chore: add coverage task to justfile and Taskfile
  - `3913d6a` — merge: chore/cliff-adopt-2026-06-11 into main
  - `77dfc33` — merge: chore/tokio-tighten into main (conflict-resolved)

## Why Absorbed

Per wave-3 directive: Metron is a substrate lib but not active in the fleet. Coverage and tokio-tighten work can be applied fleet-wide via `pheno-coverage` (when built). Cliff adoption can be applied to existing release processes.

## Active Substrate Replacements

- `pheno-otel` — OpenTelemetry-based metrics (per ADR-036 pheno-tracing is canonical)
- `pheno-context` — Metrics context propagation
- The original Metron patterns inform the Rust-side of `pheno-otel` but are not directly used

## License

MIT OR Apache-2.0 (inherited from Metron)
