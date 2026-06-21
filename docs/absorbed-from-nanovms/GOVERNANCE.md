# NanoVMS Governance

## Maintainers

NanoVMS is maintained by the Phenotype organization. The canonical
maintainer is:

- **@KooshaPari** — Project Lead, primary code owner, and release manager.

## Decision-Making

This project follows a **lazy-consensus** model:

1. **Trivial changes** (typos, formatting, CI config, docs) may be merged
   directly by the maintainer.
2. **Feature work** should be proposed via a GitHub Issue or an intent doc
   (`docs/intent/`) before implementation. Consensus is reached when no
   maintainer has objected within 72 hours.
3. **Breaking changes** require a dedicated ADR entry and at least one
   approving review from @KooshaPari.

## Contribution Process

1. All contributions must be submitted as pull requests.
2. PRs must pass the CI gate before merging.
3. Commits should follow [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `chore:`, `docs:`, `build:`, `ci:`, etc.).
4. By contributing, you agree to license your work under the project's
   MIT OR Apache-2.0 license.

## Roles

| Role           | Responsibility                                          |
|----------------|----------------------------------------------------------|
| **Maintainer** | Overall direction, code review, release management.     |
| **Contributor**| Submits PRs, files issues, participates in discussions.  |
| **Reviewer**   | Performs code review on PRs (appointed by maintainer).   |

## Release Process

1. Changes accumulate on `main`.
2. When the maintainer decides a release is warranted, a version tag
   (`v<major>.<minor>.<patch>`) is pushed.
3. The Release workflow builds binaries and publishes the GitHub Release.
4. Major version bumps (>0.x) require an ADR.

## Code of Conduct

All interactions are governed by the project's
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Harassment, trolling, and
personal attacks will not be tolerated.

---

*Last updated: 2026-06-19*
