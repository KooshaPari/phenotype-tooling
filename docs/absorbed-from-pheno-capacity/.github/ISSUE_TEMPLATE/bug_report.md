---
name: Bug report
about: Report incorrect math, broken test, or wrong anchor in pheno-capacity
title: "[bug] "
labels: ["bug", "triage"]
assignees: []
---

## Summary

<!-- One sentence: what is wrong? -->

## Reproduction

<!-- Smallest possible snippet that reproduces the issue. -->

```rust
use pheno_capacity::*;

let ctx = KvContext {
    n_layers: /* ... */ todo!(),
    n_kv_heads: /* ... */ todo!(),
    head_dim: /* ... */ todo!(),
    seq_len: /* ... */,
    batch_size: 1,
    dtype_bytes: 2,
    attention: AttentionKind::Gqa,
};

let kv_bytes = kv_cache_bytes(&ctx);
// expected: <X>
// actual:   <Y>
```

## Expected vs actual

- Expected:
- Actual:

## Anchor / reference

<!-- If you have a canonical source (paper, official config, vendor numbers), link it. -->

## Environment

- `pheno-capacity` version: <!-- v0.2.0 -->
- `rustc --version`:
- `cargo test` result:

## Logs / output

```
<paste here>
```
