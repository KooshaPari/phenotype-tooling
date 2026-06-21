# WORKLOG — pheno-capacity

Schema: pheno-worklog-schema v2.1 (per ADR-015 v2.1 bump, ADR-025).
Last updated: 2026-06-18.

| Date | Task ID | Layer | Action | Files | Device | Notes |
|---|---|---|---|---|---|---|
| 2026-06-18 | L5-105 | L5 | feat(lib): initial v0.1.0 — VRAM, model-fit, optimizer, Chinchilla | `src/lib.rs`, `src/math.rs`, `Cargo.toml`, `README.md`, `CHANGELOG.md`, `llms.txt`, `AGENTS.md`, `WORKLOG.md`, `docs/SPEC.md`, `docs/methodology.md`, `.github/workflows/ci.yml`, `.github/CODEOWNERS`, `SECURITY.md`, `LICENSE-MIT`, `LICENSE-APACHE`, `llvm-cov.toml` | macbook | ADR-035A reclassification: HwLedger bucket PAUSED→CONDITIONAL, `pheno-capacity` extracted as `pheno-*-lib` tier; 12 unit tests in `lib.rs` + 10 in `math.rs` + 5 doc tests; 100% public API coverage; `no_std` compatible; zero dependencies. |
| 2026-06-18 | L5-105 | L5 | feat(ci): no_std structural check + 80% coverage gate | `.github/workflows/ci.yml` | macbook | Adds 3rd CI job: build a `staticlib` consumer under `#![no_std]` to confirm the crate compiles without `alloc`/`std`. Coverage job enforces 80% lib tier (ADR-023 Rule 3.1). |
| 2026-06-18 | L5-105 | L5 | docs(adr): cross-link HwLedger ADR-035A | `README.md`, `docs/SPEC.md` | macbook | Reference to `apps/streamlit/lib/cost_model.py` (Python original at git `8bf878ca`) and HwLedger ADR-035A. Phase 2 of ADR-035A will migrate the Streamlit layer to call this crate. |
| 2026-06-18 | L5-105 | L5 | chore(bucket-change): HwLedger PAUSED→CONDITIONAL | (worklog only) | macbook | `bucket_change: from=PAUSED to=CONDITIONAL reason=ADR-035A (L5-105) reclassification — federated service with extractable pheno-capacity math lib` |
