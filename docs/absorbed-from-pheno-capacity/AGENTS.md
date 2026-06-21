# pheno-capacity

**Date:** 2026-06-18
**Status:** ACTIVE
**MSRV:** 1.75 (see `Cargo.toml`)
**Substrate placement:** `pheno-*-lib` (ADR-023)
**Current version:** v0.2.0 (L5-115, 2026-06-18)

## Purpose

Pure-math library for **VRAM estimation**, **model-fit scoring**, and
**hardware capacity planning** for large-language-model inference and
fine-tuning. Extracted from HwLedger per **ADR-035A** (L5-105, 2026-06-18)
and extended in **L5-115** (2026-06-18) with per-attention-kind KV cache
formulas, MoE accounting, and `BatchPolicy` selection.

The crate answers one question:

> "Given a model architecture (`params`, `n_layers`, `n_kv_heads`,
>  `head_dim`, `attention_kind`, etc.) and a target device with `D`
>  bytes of VRAM, does it fit, and how much headroom is left?"

## Build

```bash
cargo build --release
cargo test                          # 60 unit tests (default)
cargo test --features alloc         # 61 unit tests (with warning_labels)
cargo test --doc                    # 6 doc tests (canonical anchors)
cargo test --no-default-features    # no_std build (no alloc)
cargo llvm-cov --all-features --lcov --output-path lcov.info
```

## Substrate Placement

`pheno-*-lib` (ADR-023) — pure reusable Rust library; single concern
(capacity math), single crate, `no_std` compatible, zero dependencies.

## Consumers

Per ADR-035A, the intended consumers are:

- HwLedger (post Phase 2 migration): `apps/streamlit/pages/01_Planner.py`
  and `pages/07_WhatIf.py` will call `pheno_capacity::vram_estimate` and
  `model_fits_in` instead of `lib/cost_model.py::fine_tune_overhead_mb`.
- `phenotype-mcp-router`: LLM provider fit checks (per-request VRAM).
- Any future capacity-planner UI / CLI that needs VRAM math.
- `pheno-throughput` (future): TPS / TTFT math, will consume
  `AttentionKind` + `KvContext` from this crate.

## Authority

phenotype-org-governance/SUPERSEDED.md (none — first release)

## See also

- `README.md` — API surface, examples, real-world anchors.
- `docs/SPEC.md` — 1-page spec.
- `docs/methodology.md` — math methodology + source citations.
- `CHANGELOG.md` — release notes.
- `WORKLOG.md` — change history (v2.1 schema).
- `llms.txt` — agent-context summary.
- `LICENSE-MIT` / `LICENSE-APACHE` — dual license.
- Sibling: `pheno-config` (config loader), `pheno-errors`
  (canonical `AppError`), `pheno-context` (request context),
  `pheno-port-adapter` (hexagonal port trait).
