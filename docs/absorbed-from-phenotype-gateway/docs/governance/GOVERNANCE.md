# phenotype-gateway Governance

## Repository Structure

This repository is a **polyglot collection monorepo** under the
[KooshaPari](https://github.com/KooshaPari) organization.

| Area            | Language | Location                |
|-----------------|----------|-------------------------|
| Rust router     | Rust     | `packages/router/`      |
| Rust spikes     | Rust     | `spikes/rust/`          |
| Agent API       | Go       | `packages/agentapi/`    |
| Argis           | Go       | `packages/argis/`       |
| Bifrost         | Go       | `packages/bifrost/`     |
| CLI proxy       | Go       | `packages/cliproxy/`    |
| Go spikes       | Go       | `spikes/go/`            |
| Zig spikes      | Zig      | `spikes/zig/`           |
| Mojo spikes     | Mojo     | `spikes/mojo/`          |
| Third-party     | Various  | `third_party/`          |

## Commit Convention

This project uses **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `perf`, `style`.

Breaking changes append a `!` before the colon, e.g.: `feat!(scope): message`.

## Branch Strategy

- `master` — integration branch, always release-ready.
- `feat/<issue>-<slug>` — feature branches.
- `fix/<issue>-<slug>` — bug-fix branches.

## Pull Request Requirements

1. All CI checks must pass.
2. Rust crates must pass `cargo check`, `cargo fmt`, and `cargo clippy -D warnings`.
3. Go packages must pass `go vet ./...`.
4. Changes must be reviewed by the code owner(s).

## Versioning

This monorepo does **not** publish a unified version. Individual crates and
packages may version independently per semantic versioning.

## License

Licensed under **MIT OR Apache-2.0** (dual-licensed).
