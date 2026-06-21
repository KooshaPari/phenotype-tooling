# pheno-capacity

[![CI](https://github.com/KooshaPari/pheno-capacity/actions/workflows/ci.yml/badge.svg)](https://github.com/KooshaPari/pheno-capacity/actions/workflows/ci.yml)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](./LICENSE-MIT)
[![no_std](https://img.shields.io/badge/no__std-compatible-green.svg)](https://doc.rust-lang.org/reference/nomicon.html)

Pure-math library for **VRAM estimation**, **model-fit scoring**, and
**hardware capacity planning** for large-language-model inference and
fine-tuning. `no_std` compatible, zero dependencies, deterministic
pure functions.

Extracted from HwLedger (`apps/streamlit/lib/cost_model.py`,
`apps/streamlit/lib/perf_model.py` in git history @ `8bf878ca`) per
**ADR-035A** (L5-105, 2026-06-18).

## Why one crate

Before ADR-035A, the pheno-* fleet had no canonical capacity-math
library. HwLedger's Streamlit layer carried `cost_model.py` and
`perf_model.py` (Python), but those were coupled to a specific
Streamlit deployment. Any other app that wanted to ask "does
LLaMA-70B fit on 2x A100-80GB?" had to re-implement the math.

ADR-035A extracts the math into `pheno-capacity`: pure Rust, no
runtime, `no_std` compatible. Now HwLedger, `phenotype-mcp-router`,
and any future capacity-planner UI can share the same canonical
numbers.

## Quickstart

```toml
# Cargo.toml
[dependencies]
pheno-capacity = "0.2"
```

### v0.1 weights-only API (simple)

```rust
use pheno_capacity::{vram_estimate, model_fits_in, Dtype, Optimizer, optimizer_state_vram};

// How much VRAM does LLaMA-7B consume in FP16? 14 GB.
let vram = vram_estimate(7_000_000_000, Dtype::F16);
assert_eq!(vram, 14_000_000_000);

// Does LLaMA-7B FP16 fit on an A100-40GB? Yes.
let a100_40gb: u64 = 40 * 1024_u64.pow(3);
assert!(model_fits_in(7_000_000_000, a100_40gb, Dtype::F16));

// Chinchilla-optimal training tokens for a 7B model: 140B.
use pheno_capacity::chinchilla_tokens;
let tokens = chinchilla_tokens(7_000_000_000, 20.0);
assert_eq!(tokens, 140_000_000_000);
```

### v0.2 architecture-aware API (canonical)

```rust
use pheno_capacity::{
    assess_fit, estimate_vram, recommended_batch_size, AttentionKind, BatchPolicy,
    Dtype, KvContext, ModelSpec,
};

// LLaMA-3-8B: GQA, 32 layers, 8 KV heads, 128 head_dim, 4096 hidden.
let model = ModelSpec {
    params: 8_000_000_000,
    attention: AttentionKind::GQA,
    ctx_len: 8192,
    n_layers: 32,
    n_kv_heads: 8,
    head_dim: 128,
    hidden: 4096,
    quant: Dtype::F16,
    kv_quant: Dtype::F16,
    ..Default::default()
};

// Full breakdown: weights + KV + activations + overhead.
let est = estimate_vram(&model);
// Weights: 8B * 2 = 16 GB; KV at 8K ctx, batch 1: 1 GiB.
assert_eq!(est.weights, 16_000_000_000);

// Convenience: total bytes.
let total = pheno_capacity::estimate_total_vram(&model);
assert_eq!(total, est.total);

// Fit check: A100-40GB, with verdict + headroom + ratio.
let a100_40gb = 40 * 1024_u64.pow(3);
let score = assess_fit(&model, a100_40gb);
assert_eq!(score.verdict, pheno_capacity::FitVerdict::Fit);
assert!(score.headroom_bytes > 0);

// Recommended batch size (vLLM-style "fill the device").
let kv = KvContext {
    batch_size: 1,
    seq_len: 8192,
    num_layers: 32,
    num_kv_heads: 8,
    head_dim: 128,
    attention: AttentionKind::GQA,
    kv_quant: Dtype::F16,
    ..Default::default()
};
let batch = recommended_batch_size(&est, &kv, a100_40gb, BatchPolicy::FillDevice);
// LLaMA-3-8B + 1 GB KV per batch → ~24 batches fit on 40 GB.
assert!(batch >= 16, "expected >= 16, got {}", batch);
```

## API surface

| Function | Since | Purpose |
|---|---|---|
| `vram_estimate(params, dtype)` | v0.1.0 | Compute weight-only VRAM in bytes. Saturates to `u64::MAX` on overflow. |
| `model_fits_in(params, available, dtype)` | v0.1.0 | Boolean fit check. No headroom margin; caller subtracts activations/KV. |
| `optimizer_state_vram(weights_bytes, optimizer)` | v0.1.0 | Additional VRAM for fine-tuning (AdamW/LoRA/QLoRA/Adafactor). |
| `chinchilla_tokens(params, ratio)` | v0.1.0 | Chinchilla-optimal training-token budget (Hoffmann 2022). |
| `dtype_bytes(dtype)` | v0.1.0 | Byte width of a single parameter in the given dtype. |
| `Dtype::{F32, F16, BF16, I8, I4}` | v0.1.0 | The 5 canonical LLM dtypes. |
| `Optimizer::{AdamW, LoRA, QLoRA, Adafactor}` | v0.1.0 | Fine-tuning optimizer state classes. |
| `AttentionKind::{MHA, MQA, GQA, MLA, SLIDING, SSM, HYBRID, SINK}` | v0.2.0 | 8 canonical attention patterns. `Default` = GQA. |
| `AttentionKind::is_constant_in_seq()` | v0.2.0 | `true` for SSM/SLIDING/SINK (constant-in-ctx KV). |
| `KvContext` | v0.2.0 | The KV-cache-relevant context: batch, seq, layers, KV heads, head_dim, attention, etc. |
| `estimate_kv_vram(ctx, kv_quant)` | v0.2.0 | Per-attention-kind KV cache bytes. Saturates to `u64::MAX` on overflow. |
| `ModelSpec` + `MoEConfig` | v0.2.0 | Full model spec (architecture-keyed dispatch). |
| `DeviceSpec` | v0.2.0 | VRAM + display name. |
| `estimate_vram(model) -> CapacityEstimate` | v0.2.0 | Full breakdown: weights + KV + activations + overhead. |
| `estimate_total_vram(model) -> u64` | v0.2.0 | Convenience: just the total. |
| `fit_score(est, dev) -> f32` | v0.2.0 | Headroom ratio in `[0.0, 1.0]`. |
| `fit_verdict(est, dev) -> FitVerdict` | v0.2.0 | Three-way: `Fit` / `Tight` / `Fail`. |
| `assess_fit(model, vram) -> FitScore` | v0.2.0 | Convenience entry point: verdict + headroom + ratio. |
| `BatchPolicy::{FillDevice, CapBatch(n), ReserveHeadroom{ratio}}` | v0.2.0 | Batch-size selection policy. |
| `recommended_batch_size(est, ctx, vram, policy)` | v0.2.0 | Max batch size satisfying the policy. |
| `WarningFlags` + `W_MLA / W_SLIDING / W_SINK / W_SSM / W_MOE` | v0.2.0 | Bitfield of under-specified-input warnings. |
| `has_warning(flag)` / `has_any_warning()` | v0.2.0 | `no_std`-friendly check methods. |
| `warning_labels(flags) -> Vec<&'static str>` | v0.2.0 | Behind the `alloc` feature. |

## Real-world anchors

| Model | Params | Dtype | VRAM (weights only) | Source |
|---|---|---|---|---|
| LLaMA-7B | 7 B | FP16 | 14 GB | Meta 2023 |
| LLaMA-7B | 7 B | INT4 (AWQ) | 7 GB | Lin et al. 2024 |
| LLaMA-70B | 70 B | FP16 | 140 GB | Meta 2023 |
| Mixtral 8x7B | 47 B active | FP16 | 94 GB | Mistral 2024 |
| Mistral 7B | 7.3 B | FP16 | 14.6 GB | Mistral 2023 |
| Llama-3-8B | 8 B | BF16 | 16 GB | Meta 2024 |
| Llama-3-70B | 70 B | INT4 (AWQ) | 70 GB | community AWQ |

## Conventions

- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).
- rustfmt + clippy (`-D warnings`); `#![deny(missing_docs)]` on the
  public API.
- 80% lib coverage gate (ADR-023 Rule 3.1); see `llvm-cov.toml` and
  the `coverage` job in `.github/workflows/ci.yml`.
- Standalone crate (empty `[workspace]` table in `Cargo.toml`); not
  a member of the root monorepo workspace.
- Zero dependencies, `no_std` compatible.

## See also

- `docs/SPEC.md` — 1-page spec.
- `docs/methodology.md` — math methodology + source citations.
- `AGENTS.md` — agent context.
- `WORKLOG.md` — change history (v2.1 schema).
- `CHANGELOG.md` — release notes.
- `llms.txt` — agent-context summary.
- `LICENSE-MIT` / `LICENSE-APACHE` — dual license.

## License

Dual-licensed under MIT or Apache-2.0, at your option.
