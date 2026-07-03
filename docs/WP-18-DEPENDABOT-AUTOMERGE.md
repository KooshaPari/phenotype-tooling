# WP-18: Dependabot Auto-Merge Policy

Auto-merge dependabot PRs that pass required checks. Manual review for major bumps and anything affecting lockfile-sensitive crates.

## Policy

| Update type | Auto-merge | Notes |
|---|---|---|
| semver-patch (direct prod deps) | yes | `cargo update -p <name>` clean |
| semver-minor (direct prod deps) | yes | CI green + ptx gate clean |
| semver-major | no | labelled `deps:manual-review` |
| transitive-only | no | requires explicit `cargo update` PR |
| dev-dependencies | yes | ptx gate + clippy |

## Required checks before auto-merge

1. `cargo fmt --all -- --check` clean
2. `cargo clippy --workspace -- -D warnings` clean
3. `cargo test --workspace --no-fail-fast` green
4. `ptx --strict --manifest ptx.ci.toml` green
5. `coverage.yml` line coverage ≥ 80%

## Excluded crates (always manual)

- `phenotype-cli` (binary facade; breaking changes affect dispatch surface)
- `ptx` (governance wrapper; breaking changes affect gate contract)
- `phenotype-tooling-observability` (metric names locked to SLO dashboard)

## Override

Maintainers can override auto-merge by adding label `deps:block-auto-merge`. The workflow skips PRs with this label even when policy says auto-merge.