# WP-25 — Workspace Split into 3 Release Streams

## Goal

Collapse the 5 release-groups declared by WP-16 (`workspace.metadata.toml`) into 3 logical release **streams** so release-please produces independent versions per stream instead of one unified `phenotype-tooling` version.

## Stream Taxonomy

| Stream | Crates | Cadence | Release package name |
|---|---|---|---|
| **core-stream** | pt-runtime, ptx, ptx-runtime, abs-core, fcore, hashbrown, serde-ext, trait-ext, ... | weekly (breaking API bumps tagged as `1.x+`) | `phenotype-tooling-core` |
| **cli-stream** | phenotype-cli (pt binary), obs-cmd, bin/hook-entry | on-demand + release-please | `phenotype-tooling-cli` |
| **ops-stream** | phenotype-tooling-observability, phenotype-sbom-gen, release-cut | weekly (gated by signed-release.yml) | `phenotype-tooling-ops` |

The `core` + `standalone` groups from WP-16 collapse into `core-stream`. The `observability` + `release` groups collapse into `ops-stream`.

## Per-stream versioning rules

| Stream | Pre-1.0 bump | Post-1.0 bump | Breaking-API handling |
|---|---|---|---|
| `core-stream` | minor (0.3.0 → 0.4.0) | minor (1.2.0 → 1.3.0) | Explicit `feat!:` commit prefix |
| `cli-stream` | minor (0.2.0 → 0.3.0) | minor (1.0.0 → 1.1.0) | Reset to 2.0.0 on first breaking |
| `ops-stream` | patch (0.2.1 → 0.2.2) | minor (1.1.0 → 1.2.0) | `BREAKING:` trailer in commit body |

## Per-stream CHANGELOG files

- `CHANGELOG-core.md` — `phenotype-tooling-core` versions
- `CHANGELOG-cli.md` — `phenotype-tooling-cli` versions
- `CHANGELOG-ops.md` — `phenotype-tooling-ops` versions

Release-please writes each stream's CHANGELOG in its own PR (grouped by stream), keeping the cross-stream blast radius minimal.

## Per-stream tag pattern

```
phenotype-tooling-core-v0.4.0
phenotype-tooling-cli-v0.3.0
phenotype-tooling-ops-v0.2.5
```

The signed-release.yml workflow signs each tag separately and uploads per-tag assets.

## Files modified

- `workspace.metadata.toml` — collapsed 5 groups → 3 streams
- `.github/release-please-config.json` — declared `packages` map keyed by stream
- `.github/workflows/release-please.yml` — uses `group-pull-request-title-pattern` to produce per-stream PR titles
- `CHANGELOG-{core,cli,ops}.md` — per-stream changelog files (created by release-please)

## Acceptance criteria

1. `release-please.yml` produces **3 separate PRs** (one per stream) on the next push to main
2. Each PR's title is `chore(release): {{stream}} v{{version}}` (per the `group-pull-request-title-pattern`)
3. Each PR's CHANGELOG entry only lists commits from its stream's crates
4. Merging the PR triggers a per-stream tag + signed-release workflow run
5. `signed-release.yml` produces 3 separate release assets per tag

## Migration from v0.2.0 baseline

| Old | New | Notes |
|---|---|---|
| `phenotype-tooling-v0.2.0` | `phenotype-tooling-core-v0.3.0`, `phenotype-tooling-cli-v0.3.0`, `phenotype-tooling-ops-v0.3.0` | First per-stream versions |
| `crates/phenotype-cli/Cargo.toml` version | `phenotype-cli v0.3.0` | cli-stream package |
| `crates/phenotype-tooling-observability/Cargo.toml` version | `phenotype-tooling-observability v0.3.0` | ops-stream package |

The migration runs once on the next push to main after WP-25 lands. release-please detects the baseline `v0.2.0` and proposes 3 new per-stream versions.

## Related WPs

- **WP-16** — defined the 5 release groups in `workspace.metadata.toml`. WP-25 refines them to 3 streams.
- **WP-15** — release-please config. WP-25 adds the per-stream `packages` map.
- **WP-12** — signed-release.yml. WP-25 requires it to handle per-stream tags.
- **WP-20** — KMS-backed signing. Each stream's tag triggers its own KMS-backed sign run.
- **WP-21** — provenance attestation. Each stream's binary gets its own provenance bundle.
