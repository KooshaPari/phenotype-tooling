# .gitignore Adoption Guide

## TL;DR
Replace your `.gitignore` with one of the 7 templates in
[`templates/`](https://github.com/KooshaPari/phenotype-tooling/tree/main/templates).
Pick the template matching your repo's stack(s):
- `gitignore-rust` — Rust-only
- `gitignore-python` — Python-only
- `gitignore-node` — Node/TypeScript-only
- `gitignore-ios` — iOS / macOS / Swift-only
- `gitignore-mixed-rust-ios` — Rust + iOS (e.g. UniFFI, Mobius)
- `gitignore-mixed-rust-node` — Rust + Node (e.g. NAPI-RS, neon)
- `gitignore-mixed-python-node` — Python + Node (e.g. TypeScript+Python hybrid)

## Cluster detection
The CI script `scripts/check-gitignore-template.sh` auto-detects your stack by
looking for marker files (Cargo.toml → rust, pyproject.toml → python, package.json → node, *.xcodeproj → ios) and recommends a template.

## When you need more
Add stack-specific rules BELOW the imported section. Example for a Rust repo
that also uses `wasm-pack`:
```
# import gitignore-rust
/pkg/           # wasm-pack output
/www/
```

## Detection
The CI script flags any repo whose `.gitignore` is one of the trivial cluster
patterns (≤5 lines, no template reference) without a `# Source:` comment.

## Adoption sweep
As of 2026-06-11, 701 `.gitignore` files in the org. Of those, ~117 are
trivial cluster patterns (single-stack, ≤5 lines). These are the V14-T3-1e
adoption targets.
