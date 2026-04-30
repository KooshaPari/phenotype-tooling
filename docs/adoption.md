# Adoption Guide

Use `phenotype-tooling` when a repo needs reusable automation instead of another
local shell or Python script.

## Install One Tool

```bash
cargo install --path crates/quality-gate
```

## Install Into A Consumer Repo

```bash
cd /path/to/consumer-repo
bash /path/to/phenotype-tooling/scripts/adopt-tooling.sh
```

The adoption script creates `tooling/` symlinks so the consumer can invoke the
shared binaries without copying implementation code.

## Migration Rules

- Prefer Rust binaries for durable repo automation.
- Keep shell wrappers thin and temporary.
- Delete duplicated scripts once the shared binary is wired and validated.
- Record consumer adoption in that repo's worklog or session docs.

## Validation

Run the workspace checks before cutting or promoting a tool:

```bash
cargo check --workspace
cargo test --workspace
cargo clippy --workspace -- -D warnings
cargo fmt --check
```
