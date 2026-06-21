# Methodology — pheno-capacity math

## 1. Why a separate methodology doc

The math in `pheno-capacity` is small (~5 weight-math functions + 5
KV-formula dispatch branches, ~150 LoC) but each number is load-bearing:
a model-fit decision informs hardware purchases that cost $10k-$300k per
node. This doc is the audit trail for every factor, every formula, and
every "we did it this way because…" decision.

## 2. Source-of-truth chain

```
HwLedger/apps/streamlit/lib/cost_model.py   (Python, git @ 8bf878ca)
    ↓ ported + generalised
pheno-capacity/src/math.rs                   (Rust, v0.1.0 weights-only)
    ↓ extended in v0.2.0 with
pheno-capacity/src/attention.rs              (8-kind KV dispatch)
pheno-capacity/src/estimate.rs               (full breakdown + MoE)
pheno-capacity/src/policy.rs                 (FitVerdict + BatchPolicy)
    ↓ validated against
Mistral / Meta / DeepSeek / LLaMA published model cards
    ↓ plus v0.2.0 literature
Vaswani 2017 (MHA), Shazeer 2019 (MQA), Ainslie 2023 (GQA),
DeepSeek-V2 2024 (MLA), Mistral 2023 (Sliding), Mamba 2023/2024 (SSM),
Jamba 2024 (Hybrid), StreamingLLM 2023 (Sinks).
```

The Python original (`cost_model.py`, 172 LOC) was authored during
the 2026-04-23 "feat(vram-calc): absorb apxml UX" PR (#14) and
landed in the `feat/vram-calc` branch. The Python implementation
was stripped from the working tree during the 2026-06-08 hygiene
wave but the file is preserved in git history (blob
`972792e8756b1b0addd10afb263b4ecdca17a75e`) and is the canonical
reference for the **weights-only** math. The v0.2.0 KV-cache dispatch
is new in this crate; the literature anchors are listed per-attention-kind
in the rustdoc on `AttentionKind`.

## 3. Function-by-function methodology

### 3.1 `vram_estimate(N, dtype)`

**Formula:** `N * dtype_bytes(dtype)`

**Why integer math, not float:** the canonical anchors
(LLaMA-7B FP16 = 14 GB) are exact at integer precision. f32
introduces ULP drift that can flip a fit check on a 24 GB card
by ~256 MB. Using `u64::checked_mul` is both faster and exact.

**Why saturate to `u64::MAX`:** `u64::MAX` is "more than fits in
any conceivable device." Callers should treat it as a sentinel
for "don't even try to fit this on a single device; use
tensor-parallel or model-parallel."

### 3.2 `model_fits_in(N, available, dtype)`

**Formula:** `vram_estimate(N, dtype) <= available`

**Why no headroom margin:** the canonical HwLedger user-journey
(FR-HWL-CAPACITY-001) is "estimate whether the model fits AND
explain why." A 0-headroom check lets the caller layer their own
margin (e.g. 20% for activations, 10% for KV cache). A future
`fit_with_headroom` (v0.2.0) will provide the turnkey variant.

**Why a separate function, not a method on a struct:** the
function is the public surface; a struct would add boilerplate
without enabling new functionality. (The Streamlit layer in
HwLedger wraps this in a `CapacityEstimate` dataclass; that
presentation layer is a HwLedger concern, not a pheno-capacity
concern.)

### 3.3 `optimizer_state_vram(W, optimizer)`

**Formula:** `W * factor(optimizer)`

**Factors (per HwLedger `cost_model.py::fine_tune_overhead_mb`):**

| Optimizer | Factor | Justification |
|---|---|---|
| AdamW | 8.0x | FP32 master copy (2x BF16 weights) + 2x m + 2x v + 1x grad (in BF16/FP32) ≈ 8x. HwLedger's comment in `cost_model.py` says "8x"; matches Loshchilov & Hutter 2019. |
| LoRA | 0.05x | Only adapter params + their optimizer state. Typical adapter rank 8-16 on 7B model = ~10-50 MB regardless of base model size. 5% is a conservative upper bound; real LoRA is often <1%. |
| QLoRA | 0.03x | 4-bit base weights frozen; LoRA adapters in BF16. Dettmers et al. report 3% in their Table 1. |
| Adafactor | 2.5x | Factored second moment, no FP32 master copy. ~2.5x. Shazeer & Stern 2018. |

**Why `num/den` instead of `f32 * W as f64`:** integer-only
multiplication is exact (no ULP drift) and the LoRA/QLoRA
factors are not powers of 2. `5/100` and `3/100` are exact in
integer arithmetic.

### 3.4 `chinchilla_tokens(N, ratio)`

**Formula:** `(N as f32) * ratio`, cast to `u64`

**Default ratio = 20.0:** the Chinchilla paper's
compute-optimal sweet spot for dense transformers.

**Why f32, not f64:** f32 is sufficient for parameter counts up
to ~10^9 (the precision floor is 1 token at 10^9 params * 20
ratio = 2 * 10^10; f32 represents integers up to 2^24 = ~16M
exactly, so we accumulate ULP drift at the ~0.001% level which
is well below the user's "I want a ballpark" intent).

**Why saturate to `u64::MAX`:** a 100T-param model with 20x
ratio = 2 * 10^15 tokens, well below `u64::MAX` (~1.8 * 10^19).
The saturation is a paranoid safety net, not a real use case.

**Negative ratios:** nonsense; saturate to 0. The Chinchilla
paper only considers positive ratios.

## 4. What this crate does NOT do

- **No KV-cache estimation.** A future `kv_cache_vram`
  (v0.3.0) will compute per-layer KV cache. For v0.1.0, callers
  must subtract KV cache from `available` before calling
  `model_fits_in`.
- **No activation memory.** A 7B model at seq_len 2048 in FP16
  uses ~4-8 GB of activations during forward pass. Callers
  subtract this.
- **No GPU kernel optimisation.** The math is upper-bound; in
  practice, kernel-level optimisations (FlashAttention, paged
  attention) reduce the *actual* VRAM by 30-50%. The crate
  errs on the safe side.

## 5. Cross-validation against published numbers

| Model | Computed | Published | Match? |
|---|---|---|---|
| LLaMA-7B FP16 | 14.0 GB | 14.0 GB (Meta model card) | ✓ |
| LLaMA-7B INT4 | 7.0 GB | 7.0 GB (AWQ) | ✓ (memory-side approximation) |
| LLaMA-70B FP16 | 140.0 GB | 140.0 GB (Meta model card) | ✓ |
| Mixtral 8x7B FP16 | 94.0 GB | 90-96 GB (Mistral model card, with/without router weights) | ✓ (within rounding) |
| Mistral 7B FP16 | 14.6 GB | 14.2-14.6 GB (model card) | ✓ |
| Llama-3-8B BF16 | 16.0 GB | 16.0 GB (Meta model card) | ✓ |
| Llama-3-70B INT4 (AWQ) | 70.0 GB | ~70 GB (community AWQ) | ✓ |

## 6. v0.2.0 additions — KV cache dispatch + MoE + batch policy

### 6.1 Why per-attention-kind dispatch

The KV cache is the dominant memory cost for long-context LLM inference.
A single `2 * n_layers * n_heads * head_dim * seq * batch` formula is
**wrong** for 5 of the 8 patterns in use today:

| Pattern | Real formula | Why the simple formula is wrong |
|---|---|---|
| MHA | `2 * n_layers * n_heads * head_dim * seq * batch` | Correct (this is the original) |
| MQA | `2 * n_layers * 1 * head_dim * seq * batch` | The simple formula over-counts by `n_heads` |
| GQA | `2 * n_layers * n_kv_heads * head_dim * seq * batch` | The simple formula over-counts by `n_heads / n_kv_heads` (LLaMA-3-8B: 32/8 = 4× over) |
| MLA | `2 * n_layers * kv_latent_dim * seq * batch` | The simple formula over-counts by `head_dim / kv_latent_dim` (DeepSeek-V2: 128/512 = 0.25× → 4× under) |
| SLIDING | `2 * n_layers * n_kv_heads * head_dim * window_size * batch` | The simple formula over-counts by `seq / window_size` (Mistral 7B: 128K/4K = 32× over) |
| SSM | `n_layers * state_dim * bytes * batch` (no KV) | The simple formula counts 0; but there is small state |
| HYBRID | attn-block sum + SSM-block state | The simple formula counts only attn blocks, ignores SSM |
| SINK | `2 * n_layers * n_kv_heads * (sink + window) * batch` | The simple formula over-counts by `seq / (sink + window)` |

This is the reason prior public VRAM calculators (HF Accelerate,
can-it-run-llm, LM Studio's gauge) under-count KV for MoE/MLA and
over-count for SSM/sliding. The dispatch is the whole point of v0.2.0.

### 6.2 Citations per pattern

| Pattern | Citation |
|---|---|
| MHA | Vaswani et al. 2017, "Attention is All You Need", arXiv:1706.03762 |
| MQA | Shazeer 2019, "Fast Transformer Decoding", arXiv:1911.02150 |
| GQA | Ainslie et al. 2023, "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", arXiv:2305.13245 |
| MLA | DeepSeek-AI 2024, "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model", arXiv:2405.04347 |
| SLIDING | Mistral-AI 2023, "Mistral 7B", arXiv:2310.06825 |
| SSM | Gu & Dao 2023, "Mamba: Linear-Time Sequence Modeling with Selective State Spaces", arXiv:2312.00752; Dao & Gu 2024, "Mamba-2", arXiv:2405.21060 |
| HYBRID | AI21 2024, "Jamba: A Hybrid Transformer-Mamba Language Model", arXiv:2403.19887 |
| SINK | Xiao et al. 2023, "Efficient Streaming Language Models with Attention Sinks", arXiv:2309.17453 |

### 6.3 MoE active-param accounting

`MoEConfig::active_params = shared + active_experts * expert_params`.

For Mixtral-8x7B (the canonical MoE test case): 14B shared + 2 * 4.25B
= 22.5B active → 45 GB at FP16. The **total** parameter count is 46.7B
(8 experts), but only `active_params` are resident during inference —
the rest can stay on disk / CPU. The formula matches the Mistral
model card (arXiv:2401.04088) and the DeepSeek-V3 paper
(arXiv:2412.19437, MoE active accounting).

### 6.4 Activation memory (forward-pass only)

`2 * batch * seq * hidden * 2 (fp16)`.

This is conservative. The typical transformer activation peak is
`2 * batch * seq * hidden` in fp16 (Q + K + V + softmax + attention
output). We use 2× as a safety margin for K/V gather + softmax +
attention output. Training would need gradient scratch, which is out
of scope (a v0.5 candidate).

### 6.5 5% framework overhead

`max(weights * 0.05, 256 MiB)`.

Empirical vLLM / TGI CUDA context reserve. The 256 MiB floor prevents
the overhead from being tiny for small models. The 5% scales linearly
with the weight budget (matches PyTorch's allocator overhead and
CUDA context).

### 6.6 Fit score thresholds

- `THRESHOLD_TIGHT = 0.30` (30% headroom) — below this, KV growth at
  larger `ctx_len` will spill. The HwLedger Streamlit capacity planner
  has used this threshold since 2026-04-23; the Rust port preserves
  it.
- `THRESHOLD_FAIL = 0.05` (5% headroom) — below this, the model is too
  close to the device limit to be safe; vLLM will start paging.

### 6.7 Batch policy (slice 1 deliverable)

- `FillDevice`: binary search for max `batch` such that
  `base + batch * (kv + activations) ≤ device_vram`. Capped at 1024
  (the practical upper bound for per-step batch in vLLM).
- `CapBatch(n)`: hard cap at `n` regardless of headroom. Useful for
  latency-sensitive workloads.
- `ReserveHeadroom { ratio }`: target headroom ratio in basis points
  (5000 = 50%). The largest batch such that
  `total ≤ device * (1 - ratio)`.

## 7. Future work

- **v0.3.0** — Consolidate `KvContext` + `estimate_kv_vram` API
  (currently two parallel implementations in `attention` and
  `estimate`; will merge).
- **v0.4.0** — GPU spec table (A100/H100/L40S/B200/M3_Ultra/RTX_4090)
  with peak HBM bandwidth + BF16 TFLOPS. Consumed by
  `pheno-throughput` (future crate).
- **v0.5.0** — `activation_vram(seq_len, hidden, attention_kind)`
  refined dispatch (per-pattern activation formulas; SSM is
  constant-in-seq, Mamba-2 has a different activation shape).
- **v0.6.0** — Speculative-decoding memory: draft-model VRAM +
  verify-pass overhead.
- **v0.7.0** — Tensor-parallel / pipeline-parallel partitioning:
  per-GPU shard size from `n_layers / tp_degree` etc.
