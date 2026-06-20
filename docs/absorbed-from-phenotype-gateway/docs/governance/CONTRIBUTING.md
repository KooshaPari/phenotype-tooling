# Contributing to phenotype-gateway

## Prerequisites

- Rust toolchain (`cargo`, `rustc`) — install via [rustup](https://rustup.rs)
- Go toolchain (`go`) — install via [go.dev](https://go.dev/dl)
- [just](https://github.com/casey/just) — command runner
- [go-task](https://taskfile.dev) — existing task runner (used via `Taskfile.yml`)
- `cargo-deny` — `cargo install cargo-deny` (optional, for audits)

## Quick Start

```shell
# Check all Rust crates
just check

# Run all Rust tests
just test

# Lint all Rust crates
just lint

# Run Go vet on all Go packages
just go-vet

# Full pre-flight suite
just all
```

## Smoke Tests

Existing smoke tests are defined in `Taskfile.yml`:

```shell
# Go smoke (all third_party + packages anchors)
task smoke

# Rust router smoke
task router:test

# Full smoke
task smoke:all
```

## Code Quality

### Rust

- Run `cargo clippy --all-targets -- -D warnings` on each crate before pushing.
- Run `cargo fmt --all` to format.
- New features must include tests.
- No `unsafe` code unless absolutely necessary (document with `SAFETY:` comments).

### Go

- Run `go vet ./...` in each Go module before pushing.
- Run `go fmt ./...` to format.
- Follow [Go Proverbs](https://go-proverbs.github.io/).

## Pull Request Process

1. Create a branch from `master` with conventional naming:
   - `feat/<issue>-<slug>` for features
   - `fix/<issue>-<slug>` for fixes
2. Make changes, ensuring all CI checks pass.
3. Open a PR against `master`.
4. Ensure the PR description references the relevant issue or ADR.
5. Squash-merge when approved.

## Questions?

Open an issue or reach out to the repository owner.
