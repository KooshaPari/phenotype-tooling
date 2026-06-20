# Contributing to pheno-errors

Thank you for your interest in contributing to `pheno-errors`!

## Getting Started

1. Ensure you have Rust 2021 edition or later installed.
2. Clone the repository and run `cargo test` to verify the build.
3. Familiarise yourself with the crate's design: see `ARCHITECTURE.md` and `SPEC.md`.

## Design Principles

- **5-variant limit**: `AppError` is intentionally closed at 5 variants. Growing beyond 5 requires a breaking change — open an issue first.
- **No blanket `From<E: Error>`**: Callers must explicitly map their error types.
- **Minimal dependencies**: Only `thiserror`, `anyhow`, and `tracing` in production.
- **Structured context**: Use `Kind()` for metrics/logs routing, not string parsing.

## Pull Request Process

1. Create a feature branch from `main`.
2. Add tests for any new functionality.
3. Run `cargo test` and `cargo clippy -- -D warnings` before submitting.
4. Update `CHANGELOG.md` with your change under the `Unreleased` section.
5. Open a PR — maintainers will review within 48 hours.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `chore:` — maintenance, tooling, governance
- `refactor:` — code restructuring
- `test:` — test additions or changes

## Code of Conduct

All participants must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
