# Contributing

Thanks for your interest in contributing. This repo is **archived** and
superseded by [OmniRoute](https://github.com/KooshaPari/OmniRoute). New
contributions should target OmniRoute.

If you must make changes here:

1. Fork the repository.
2. Create a feature branch (`feat/<short-name>` or `chore/<short-name>`).
3. Run `just ci` locally — it must pass.
4. Open a pull request against `main`.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `chore:` maintenance / hygiene
- `docs:` documentation only
- `ci:` CI / workflow changes

## Code Style

- Rust: `cargo fmt` + `cargo clippy -- -D warnings`
- Editor: see `.editorconfig` (tabs, indent size 2)
- Shell: `set -euo pipefail` at the top of every `.sh` file
