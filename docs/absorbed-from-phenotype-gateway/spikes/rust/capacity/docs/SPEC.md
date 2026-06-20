# SPEC — pheno-capacity

**Status:** v0.1.0 (2026-06-18)
**Source of truth:** `pheno_capacity` Rust crate
**Authority:** ADR-035A (L5-105, 2026-06-18)

## 1. Problem statement

The pheno-* fleet (HwLedger, `phenotype-mcp-router`, and future
capacity-planner UIs) needs a canonical, side-effect-free, reusable
implementation of LLM capacity math:

1. **VRAM estimation** — how many bytes does a model with `N`
   parameters consume in a given dtype?
2. **Model-fit scoring** — does a model fit on a target device?
3. **Optimizer-state overhead** — how much extra VRAM does
   fine-tuning add on top of the forward-pass weight footprint?
4. **Training-token budgeting** — what is the Chinchilla-optimal
   token count for a given parameter size?

Before v0.1.0, the answers lived in HwLedger's Python
`cost_model.py` and `perf_model.py`. These were (a) coupled to a
specific Streamlit deployment, (b) Python-only, (c) not exposed to
any other consumer. ADR-035A extracts the math into a standalone
Rust crate.

## 2. Non-goals

- **Throughput / TPS / TTFT estimation**: out of scope; lives in a
  future `pheno-throughput` crate.
- **GPU pricing / cost-to-train**: out of scope; lives in
  HwLedger as policy data.
- **Layer-by-layer memory profiling**: out of scope; requires a
  model graph.
- **Hardware probing / vendor SDKs**: out of scope; HwLedger
  owns that surface.
- **Distributed-training strategies** (ZeRO, FSDP, TP): out of
  scope; the model-fit check assumes single-device or naive
  tensor-parallel.

## 3. Public API (v0.1.0)

```rust
// src/lib.rs re-exports from src/math.rs
pub mod math;
pub use math::{
    chinchilla_tokens, dtype_bytes, model_fits_in,
    optimizer_state_vram, vram_estimate, Dtype, Optimizer,
};

pub enum Dtype { F32, F16, BF16, I8, I4 }
pub enum Optimizer { AdamW, LoRA, QLoRA, Adafactor }

pub const fn vram_estimate(model_params: u64, dtype: Dtype) -> u64;
pub const fn model_fits_in(model_params: u64, available: u64, dtype: Dtype) -> bool;
pub fn optimizer_state_vram(weights_bytes: u64, optimizer: Optimizer) -> u64;
pub fn chinchilla_tokens(parameter_count: u64, ratio: f32) -> u64;
pub const fn dtype_bytes(d: Dtype) -> u8;
```

## 4. Math contract

| Function | Formula | Edge case | Overflow behaviour |
|---|---|---|---|
| `vram_estimate(N, d)` | `N * dtype_bytes(d)` | `N == 0` → `0` | `checked_mul`; saturate to `u64::MAX` |
| `model_fits_in(N, A, d)` | `vram_estimate(N, d) <= A` | `A == 0` → `false` (any positive N) | Saturated `vram` → `false` |
| `optimizer_state_vram(W, o)` | `W * (num/den)` per optimizer | `W == 0` → `0` | `checked_mul`; saturate to `u64::MAX` |
| `chinchilla_tokens(N, r)` | `N * r` (f32 → u64) | `r <= 0` → `0`; `r == 0` → `0` | Saturated f32 → `u64::MAX` |
| `dtype_bytes(d)` | lookup table | exhaustive | n/a |

### 4.1 Optimizer factors

| Optimizer | num | den | factor | Source |
|---|---|---|---|---|
| `AdamW` | 8 | 1 | 8.0x | Loshchilov & Hutter 2019; matches HwLedger `cost_model.py::fine_tune_overhead_mb` |
| `LoRA` | 5 | 100 | 0.05x | Hu et al. 2021 |
| `QLoRA` | 3 | 100 | 0.03x | Dettmers et al. 2023 |
| `Adafactor` | 5 | 2 | 2.5x | Shazeer & Stern 2018 |

## 5. Quality bar

Per ADR-023 Rule 3.1 (lib tier):

- 80% line coverage minimum (`llvm-cov`).
- 100% public-API doc-tested (5 doc tests in v0.1.0).
- `no_std` compatible; zero dependencies.
- `#![deny(missing_docs)]` on the public API.
- `cargo test --all-features` clean.
- `cargo clippy -- -D warnings` clean.
- `cargo fmt --check` clean.

## 6. Versioning

| Version | When | Notable |
|---|---|---|
| 0.1.0 | 2026-06-18 | Initial release. VRAM, model-fit, optimizer, Chinchilla. |
| 0.2.0 | (planned) | `fit_with_headroom` for turnkey fit-check. |
| 0.3.0 | (planned) | `kv_cache_vram` for transformer inference. |
| 0.4.0 | (planned) | GPU spec table + `pheno-throughput` integration. |

## 7. Consumers (planned)

- HwLedger Streamlit Planner / WhatIf pages (Phase 2 of ADR-035A).
- `phenotype-mcp-router`: LLM provider fit checks.
- `pheno-throughput` (future): TPS/TTFT estimation.

## 8. Authority chain

- **ADR-035A** — reclassification + extraction rationale.
- **ADR-023** — agent-effort governance, lib tier quality bar.
- **AGENTS.md** — fleet-level conventions.
- **pheno-worklog-schema v2.1** — `WORKLOG.md` schema.

## 9. References

- Hoffmann et al. 2022, "Training Compute-Optimal Large Language Models" (Chinchilla), arXiv:2203.15556.
- Loshchilov & Hutter 2019, "Decoupled Weight Decay Regularization" (AdamW), arXiv:1711.05101.
- Hu et al. 2021, "LoRA: Low-Rank Adaptation of Large Language Models", arXiv:2106.09685.
- Dettmers et al. 2023, "QLoRA: Efficient Finetuning of Quantized LLMs", arXiv:2305.14314.
- Lin et al. 2024, "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", arXiv:2306.00978.
- HwLedger `apps/streamlit/lib/cost_model.py` (Python original, git @ `8bf878ca`).
