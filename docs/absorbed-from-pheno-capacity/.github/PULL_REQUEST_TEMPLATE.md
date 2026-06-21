<!-- .github/PULL_REQUEST_TEMPLATE.md — pheno-capacity -->

## Summary

<!-- One-paragraph summary of what this PR does and why. Cite ADR IDs when relevant (e.g. ADR-023, ADR-035A). -->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Chore / governance (CODEOWNERS, templates, CI, etc.)
- [ ] Refactor (no functional change)

## Scope

<!-- Which crate(s) / module(s) does this PR touch? -->

- [ ] `src/lib.rs` (public API)
- [ ] `src/kv_cache.rs`
- [ ] `src/vram.rs`
- [ ] `src/model_fit.rs`
- [ ] `src/moe.rs`
- [ ] `src/optimizer.rs`
- [ ] `src/batch.rs`
- [ ] `src/chinchilla.rs`
- [ ] `src/attention.rs`
- [ ] `src/spec.rs`
- [ ] docs/
- [ ] CI / governance (`.github/`, `justfile`)

## ADR / spec linkage

<!-- Reference the relevant ADR or spec section. -->

- ADR: <!-- ADR-XXX -->
- Spec: <!-- docs/SPEC.md §X -->

## Verification

<!-- Run locally before requesting review. Paste command + result summary. -->

- [ ] `cargo check --all-targets` passes
- [ ] `cargo test` passes (60 unit tests)
- [ ] `cargo test --features alloc` passes (61 unit tests)
- [ ] `cargo test --no-default-features` passes (`no_std` build)
- [ ] `cargo test --doc` passes (6 doc tests)
- [ ] `cargo fmt --all -- --check` passes
- [ ] `cargo clippy --all-targets --all-features -- -D warnings` passes
- [ ] `cargo llvm-cov --all-features` shows ≥80% line coverage (lib tier per ADR-023)

## Real-world anchors

<!-- If your change touches VRAM math, KV cache, MoE, or Chinchilla, list the
real-world model(s) you re-ran through the crate to confirm numbers match
the canonical references in docs/methodology.md. -->

- Model:
- VRAM (this crate):
- VRAM (reference):
- Delta:

## Checklist

- [ ] I have read `CONTRIBUTING.md` (or its absence is intentional — see CODEOWNERS)
- [ ] My change is covered by tests (unit, doc, or both)
- [ ] I have updated `CHANGELOG.md` under "Unreleased"
- [ ] I have not introduced new warnings (`cargo clippy`)
- [ ] I have not bumped the version (leave to release-manager)
- [ ] `git commit` message follows Conventional Commits (`feat(...)`, `fix(...)`, `chore(...)`)
