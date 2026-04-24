# Contributing to phenotype-tooling

Standardized Phenotype enterprise contribution guidelines.

## Development Workflow

- Follow the branch-based delivery protocol described in `CLAUDE.md` / `AGENTS.md`.
- Ensure `cargo fmt --all -- --check`, `cargo clippy --workspace -- -D warnings`,
  and `cargo test --workspace` pass locally before opening a PR.
- Document user-facing changes in `CHANGELOG.md` under the `[Unreleased]` section.
- AgilePlus spec references are required for non-trivial work; see
  `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`.

## Commit Style

Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`).
