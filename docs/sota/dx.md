# DX — SOTA (phenotype-tooling)

## Workflow (chosen)

1. `cargo check --workspace` from repo root
2. Install tool: `cargo install --path crates/quality-gate`
3. Adopt in consumer repo: `bash scripts/adopt-tooling.sh`
4. For absorbed subdirs, build per README in `crates/<name>/`

```bash
cargo check --workspace
cargo test --workspace
cargo install --path crates/quality-gate
```

## Alternatives considered

| Alternative | Verdict |
|-------------|---------|
| Per-repo script copies | rejected |
| **Rust workspace + adopt shims** | **chosen** |

## Evolution triggers

- New crate added → update README crate table + OKF
