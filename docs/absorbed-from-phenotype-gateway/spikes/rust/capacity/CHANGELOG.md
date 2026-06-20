# Changelog

All notable changes to `pheno-capacity` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Absorbed into phenotype-gateway 2026-06-19 (L5-117)

**Source:** `KooshaPari/pheno-capacity` v0.2.0 (created 2026-06-18, ~24h before absorb)
**Pattern:** `phenotype-gfx` 4-repo absorb (L5-109..L5-112, 2026-06-18)
**Decision doc:** [`findings/2026-06-19-L5-117-pheno-capacity-collection-merge.md`](https://github.com/KooshaPari/phenotype-apps/blob/main/findings/2026-06-19-L5-117-pheno-capacity-collection-merge.md)
**ADR:** ADR-036 (pheno-capacity absorb into phenotype-gateway)

This is the 9th absorb in the L5-109 wave and the **first `pheno-*-lib`**. The math lib is hosted as `spikes/rust/capacity/` (crate name `phenotype-capacity-spike`, mirroring the existing `phenotype-router-spike` precedent at `spikes/rust/router/`). The published `pheno-capacity = "0.2"` crates.io artifact remains as a stable shim (OQ-1).

After this PR merges, `KooshaPari/pheno-capacity` will be archived (read-only) per the 4-repo retirement pattern (L5-109). 90-day GitHub retention before hard-delete is possible via the GitHub UI.

## [Unreleased]

### Planned
- v0.3.0: `kv_cache_vram(num_layers, num_heads, head_dim, seq_len, batch, dtype)`
  — KV-cache memory estimator for transformer inference (deprecated by v0.2.0
  `KvContext`; v0.3 will consolidate the API).
- v0.4.0: GPU spec table (A100/H100/L40S/B200/M3_Ultra/RTX_4090) with peak
  HBM bandwidth and BF16 TFLOPS; consumed by `pheno-throughput` (future crate).

## [0.2.0] - 2026-06-18

### Added
- **Attention architecture dispatch** (`AttentionKind`): 8 canonical patterns
  — MHA, MQA, GQA, MLA, SLIDING, SSM, HYBRID, SINK. Each has a distinct
  KV cache formula; `Default` is GQA (the post-2023 dominant pattern).
  Method: `is_constant_in_seq()` for SSM / SLIDING / SINK vs linear-in-seq.
- **`KvContext`** struct + **`estimate_kv_vram(ctx, kv_quant) -> u64`**:
  per-attention-kind KV cache estimator. Doc-tested against
  LLaMA-3-8B at 8K ctx (1 GiB), DeepSeek-V2-Lite MLA at 32K ctx
  (1.65 GiB), Mamba-2-2.7B SSM (16 KB state), Mistral SLIDING
  (window-bound at 4096).
- **`ModelSpec`** + **`estimate_vram(spec) -> CapacityEstimate`**: full
  architecture-keyed VRAM estimate (weights + KV + activations + overhead).
  Field-by-field maps to `AttentionKind` (e.g., `kv_latent_dim` for MLA,
  `state_dim` for SSM, `window_size` + `sink_tokens` for SINK).
- **`DeviceSpec`** + **`fit_score(est, dev) -> f32`** + **`fit_verdict(...) -> FitVerdict`**:
  headroom-ratio and three-way fit judgment (Fit / Tight / Fail).
  Thresholds: 30 % headroom for Fit, 5 % for Fail.
- **`MoEConfig`**: MoE active-param accounting
  (`active = shared + active_experts * expert_params`). Saturates on overflow.
  Tested against Mixtral-8x7B.
- **`estimate_total_vram(spec) -> u64`**: convenience returning just the total.
- **`FitScore` struct + `assess_fit(spec, vram) -> FitScore`**: convenience
  entry point returning verdict + headroom_bytes + fit_score.
- **`BatchPolicy` + `recommended_batch_size(...)`**: FillDevice / CapBatch /
  ReserveHeadroom variants. Iterative binary-search for max batch.
- **`WarningFlags`** bitfield (5 conditions: W_MLA, W_SLIDING, W_SINK, W_SSM,
  W_MOE) for under-specified inputs. `has_warning(flag)` and
  `has_any_warning()` are `no_std`-friendly. Optional `warning_labels(flags) -> Vec<&str>`
  behind the `alloc` feature.
- 60 unit tests (all passing) + 6 doc tests. Coverage: MHA/MQA/GQA/MLA/SLIDING/
  SSM/HYBRID/SINK dispatch, MoE accounting, fit-score boundary, headroom
  reserve, batch-size policy.
- New Cargo feature `alloc` enables `warning_labels` (gated). Core math
  remains `no_std`-compatible with zero dependencies.

### Changed
- Bumped to v0.2.0 (minor version: new public API surface). Crate is
  source-compatible with v0.1.0 consumers (all v0.1.0 functions retained).
- Expanded keywords: added `attention`, `kv-cache`, `moe`.

## [0.1.0] - 2026-06-18

### Added
- `vram_estimate(model_params, dtype) -> u64`: weight-only VRAM in bytes.
  Saturates to `u64::MAX` on overflow. Doc-tested against LLaMA-7B FP16
  (14 GB), LLaMA-70B FP16 (140 GB), LLaMA-7B INT4 AWQ (7 GB).
- `model_fits_in(model_params, available, dtype) -> bool`: boolean
  fit check. No headroom margin (caller subtracts activations/KV).
  Doc-tested against A100-40GB, RTX-4090-24GB, M3-Ultra-192GB, 2x
  A100-80GB tensor-parallel.
- `optimizer_state_vram(weights_bytes, optimizer) -> u64`: additional
  VRAM for fine-tuning. Supports `Optimizer::{AdamW, LoRA, QLoRA,
  Adafactor}`. Doc-tested at 1 GB BF16 baseline.
- `chinchilla_tokens(parameter_count, ratio) -> u64`:
  Chinchilla-optimal training-token budget (Hoffmann 2022). Default
  ratio = 20 (compute-optimal); 4-8 typical for continued-pretraining.
- `dtype_bytes(dtype) -> u8`: byte width per parameter.
- `Dtype::{F32, F16, BF16, I8, I4}`: 5 canonical LLM dtypes.
- `Dtype::ALL: &[Dtype; 5]`: exhaustive list.
- `Dtype::as_str() -> &'static str`: human-readable name.
- `Optimizer::{AdamW, LoRA, QLoRA, Adafactor}`: fine-tuning classes.
- 12 inline unit tests in `src/lib.rs` + 10 in `src/math.rs` + 5 doc tests.
- `no_std` compatible (`#![cfg_attr(not(test), no_std)]`); zero
  dependencies.
- CI: `cargo test --all-features` + `cargo llvm-cov` coverage job.
- Meta-bundle: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `llms.txt`,
  `WORKLOG.md`, `docs/SPEC.md`, `docs/methodology.md`, dual
  `LICENSE-MIT` + `LICENSE-APACHE`, `CODEOWNERS`, `SECURITY.md`.

### Source / lineage

Ported from HwLedger `apps/streamlit/lib/cost_model.py` (172 LOC,
git @ `8bf878ca`) and `apps/streamlit/lib/perf_model.py` (120 LOC).
Per ADR-035A Phase 1, the math is re-implemented in Rust with
`no_std` compatibility, deterministic pure functions, and explicit
overflow handling.
