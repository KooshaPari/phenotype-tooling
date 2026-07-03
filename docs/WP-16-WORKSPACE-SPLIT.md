# WP-16 — Workspace Split for Per-Crate Versioning

**Branch:** `refactor/wp16-workspace-split`
**Depends on:** WP-15 (release-please)
**Unblocks:** independent per-group releases, smaller changelogs, targeted
backports without forcing a workspace-wide version bump.

## Goal

Decompose the single-package `phenotype-tooling` workspace into a set of
**release groups** so that release-please can bump a subset of crates when
only those crates changed. Today every push to `main` would force a single
`phenotype-tooling` version bump — that couples unrelated changes and produces
noisy changelogs. WP-16 introduces `release-group` taxonomy + per-group semver.

## Taxonomy (4 groups)

| Group         | Crates                                                                                                                                                                                          | Bump rule                                |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| `core`        | `phenotype-cli`, `phenotype-config`, `phenotype-diff`, `phenotype-tooling-observability`, `phenotype_platform`, `phenotype_ontology`, `phenotype_pdk`, `acceptance-contract`, `agent-orchestrator`, `dag-scheduler`, `worktree-manager`, `phenotype-cli-bin` | Semver bumps per group. Breaking intra-group → minor. |
| `cli`         | `phenotype-tooling-observability` (CLI surface), `audit-implementation`, `audit-privacy`, `bench-guard`, `commit-msg-check`, `doc-link-check`, `legacy-scan`                                       | Semver bumps per group. Breaking intra-group → minor. |
| `observability` | `phenotype-tooling-observability`, `sbom-gen`, `criterion-bench`                                                                                                                                  | Patch + minor only; major reserved for SLO schema breaks. |
| `release`     | `release-cut`, `ptx`, `signed-release` (in `signed-release.yml` workflow)                                                                                                                          | Patch + minor only; runs of the signing pipeline. |

> Note: a single crate may appear in multiple groups. Annotation is the
> source of truth; the taxonomy table is informational only.

## Files

- **`workspace.metadata.toml`** — groups table mapping `group-name -> { members: [...], tag: "vX.Y.Z", bump: "patch|minor|major" }`.
- **`crates/*/Cargo.toml`** — each crate annotated with
  `[package.metadata.release-group] = "<group>"`. The annotation is added by
  `_wp16_annotate.py` (idempotent — only inserts the field if absent).
- **`docs/WP-16-WORKSPACE-SPLIT.md`** — this doc.

## Migration

`phenotype-tooling` v0.2.0 (already tagged) is the **last unified release**.
The first release-please run after this WP lands will:

1. Detect the existing `v0.2.0` tag
2. Read the workspace metadata + each crate's `release-group` annotation
3. Propose the **lowest** per-group bump across the touched crates
4. Open a release PR that updates version fields for the touched groups +
   appends to `CHANGELOG.md`

A group with no touched crates keeps its prior version — independent releases
become possible.

## Acceptance criteria

- [x] `workspace.metadata.toml` parses cleanly with `tomllib` and lists
      all 4 groups + their members
- [x] Each crate under `crates/*/Cargo.toml` has
      `[package.metadata.release-group]` set
- [x] `cargo check --workspace` exits 0 (the annotation is additive metadata,
      not a code change)
- [x] `cargo metadata --format-version=1` surfaces the `release-group` values

## Future work

- **WP-16b**: bootstrap per-group CI so `cargo test -p release-group` runs
  only the affected crates (eliminates 4m27s workspace-wide builds on PRs
  that touch a single group).
- **WP-16c**: per-group SBOM publication so each release group's tag
  ships with its own CycloneDX SBOM (today SBOM is workspace-wide).
