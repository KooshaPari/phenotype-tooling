# HeliosBench port

**Source:** `KooshaPari/heliosBench`  
**Date:** 2026-06-17  
**Target owner:** `phenotype-tooling` (CLI benchmark harness boundary)

## Paths

- `absorption/helios-bench/` — absorption boundary stub
- `crates/heliosbench/` — interim subtree merge (Python benchmark harness)

`portage` does **not** supersede this harness — different domain. Repoint
`helios-router` and `helios-cli` manifests after full absorption.

This stub closes the Batch 3 archive gate per
`phenotype-registry/docs/operations/BATCH3_ROLE_JUSTIFICATION.md`.
