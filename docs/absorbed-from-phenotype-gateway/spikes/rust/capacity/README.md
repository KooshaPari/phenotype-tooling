# Rust spike — capacity math (H14+ scaffold, L5-117)

**Source:** Absorbed from [`KooshaPari/pheno-capacity`](https://github.com/KooshaPari/pheno-capacity) v0.2.0 (2026-06-19) per **L5-117** (collection-repo merge plan: `findings/2026-06-19-L5-117-pheno-capacity-collection-merge.md`).

**Pattern reference:** `phenotype-gfx` 4-repo absorb (L5-109..L5-112, 2026-06-18) — single Cargo package, multi-module, no parent workspace.

## Goal

Provide pure-math capacity-planning for the gateway's intelligent routing layer (H6+): given a model + a target device, does it fit? Given a device + an inference rate, what is the throughput? Given a workload, which provider hardware pool can serve it?

This spike is the **second Rust spike** in `phenotype-gateway/spikes/rust/` (the first being the router spike; the two are complementary, not duplicative).

## What is in the absorb

- 5 source files (`src/pheno_capacity/{lib,math,attention,policy,estimate}.rs`, ~2,200 LOC)
- Pure functions, `no_std` compatible, zero dependencies, deterministic
- 60 unit tests + 6 doc tests (all pass at source v0.2.0)
- 80%+ line coverage (lib tier per ADR-023 Rule 3.1)

## What lives elsewhere

- **Spec / methodology**: `docs/SPEC.md` (4.9 KB), `docs/methodology.md` (12 KB) — these are absorbed into the spike's docs/ directory.
- **Meta-bundle**: `AGENTS.md`, `CHANGELOG.md`, `WORKLOG.md`, `llms.txt`, `LICENSE-{MIT,APACHE}`, `SECURITY.md`, `llvm-cov.toml` — at the spike root.
- **CI**: `.github/workflows/cargo.yml` (gateway root) — translated from the source pheno-capacity CI.

## Pairing with the router spike

| Spike | Question it answers |
|---|---|
| `spikes/rust/router/` | Given a request, which model endpoint serves it? |
| `spikes/rust/capacity/` | Given a model + a target device, does it fit? |

Together they enable provider-aware fit-checked routing (e.g. "route to deepseek-r1 because the request needs a 70B model and only 2x A100-80 has the VRAM").

## Status

`spikes/rust/capacity/` — **H14+ scaffold** (absorb complete; awaiting H6+ roadmap integration).

## Open questions (see L5-117 plan §7)

- OQ-1: keep the published `pheno-capacity = "0.2"` crates.io artifact as a stable shim (recommended).
- OQ-4: keep this subcrate standalone, do not introduce a Cargo workspace at the gateway root.
- OQ-5: promotion to `packages/capacity/` requires `GATEWAY_FEATURE_PARITY.md` (deferred).
