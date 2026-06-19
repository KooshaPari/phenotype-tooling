# Absorbed from helios-router — 2026-06-18

**Source:** `KooshaPari/helios-router` (deleted 2026-06-18)
**Target:** `KooshaPari/phenotype-tooling/docs/absorbed-from-helios-router/`

## What Was Here

helios-router was a local Rust router with hexagonal port/adapter layout:
- `src/` — Rust port/adapter code
- `.archive/dashboard/` — React UI for visualizing routing decisions
- `Cargo.toml`, `Justfile`, `Taskfile.yml` — build/task config

## Prior Absorptions

- UI components (`RoutingTable.tsx`, `ParetoChart.tsx`, `mockData.ts`) → `helios-cli/tools/dashboard/` (S19)
- Architecture intent + boundary doc → main (PR #230)

## Why Deleted

helios-router was archived. Active router work happens in:
- `Tokn` (Rust routing substrate, per ADR-001)
- `phenotype-voxel` (UI/routing front-end)
- `helios-cli` (CLI consumer; now also hosts UI components)

The Rust core from helios-router is captured here for reference but is not actively maintained.

## License

MIT (inherited from helios-router)
