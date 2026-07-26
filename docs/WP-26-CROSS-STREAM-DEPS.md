# WP-26 — Cross-Stream Dependency Graph + Bump-Broadcast

## Why this WP exists

WP-25 split the monorepo into three release streams (`core`, `cli`, `ops`).
release-please now proposes three independent versions per main push. Without
a cross-stream bump-broadcast rule, a `core` minor bump can break `cli` or
`ops` if either stream depends on a `core` crate and the API changed.

WP-26 closes that loop by computing the **cross-stream dep graph** on every
PR, exposing it as a JSON artifact, and using it as the signal release-please
(or a future `pt dependency-bump` subcommand) consumes when deciding whether
to nudge downstream streams as part of a single release PR.

## Deliverables (this WP)

| File | Purpose |
|---|---|
| `scripts/cross_stream_deps.py` | Pure-python helper: parses `workspace.metadata.toml`, invokes `cargo metadata`, walks per-crate `[dependencies]`, emits `.github/cross-stream-dependencies.json`. |
| `.github/workflows/cross-stream-bump.yml` | Runs the helper on every PR + main push. `--check` mode in PR context fails the build if the regenerated graph differs from the committed one (drift detector). Main push mode overwrites the artifact. Posts a per-PR comment summarising the cross-stream edges. |
| `docs/WP-26-CROSS-STREAM-DEPS.md` | This document. |
| `.github/cross-stream-dependencies.json` | The artifact itself — must be committed so release-please can read it without a network round-trip. |

## Algorithm

1. **Parse workspace metadata.** `workspace.metadata.toml` is the source of
   truth for "which crate lives in which release-stream".
2. **Resolve the dependency graph.** `cargo metadata --format-version 1 --no-deps`
   walks workspace internals only (external crates are filtered out).
3. **Classify edges by stream.** For each edge `(from_crate, to_crate)`,
   look up `from_crate → release-group → release-stream`. Same-stream edges
   are recorded as `cross_stream: false`. Cross-stream edges are
   `cross_stream: true`.
4. **Aggregate.** Count cross-stream edges per source stream. This is the
   "stream bump pressure" metric a future WP-26-extension can use to
   drive release-please's "bump downstream" hook.

## CLI

```bash
# regenerate the artifact
python scripts/cross_stream_deps.py

# CI: fail if the artifact on disk is stale (used in PR mode)
python scripts/cross_stream_deps.py --check

# custom output / manifest paths
python scripts/cross_stream_deps.py \
  --out custom/path/deps.json \
  --manifest workspace.metadata.toml
```

Exit codes: `0` ok, `1` cargo metadata failed, `2` workspace metadata
unparseable, `3` write failed, `4` drift detected.

## Output schema (`.github/cross-stream-dependencies.json`)

```jsonc
{
  "schema_version": 1,
  "edges": [
    {
      "from_crate": "phenotype-cli",
      "from_stream": "cli",
      "to_crate": "phenotype-config",
      "to_stream": "core",
      "kind": "normal",
      "cross_stream": true
    }
  ],
  "summary": {
    "edges_total": 42,
    "cross_stream_edges": 19,
    "by_from_stream": {"core": 7, "cli": 9, "ops": 3},
    "stream_targets_required": {"core": 0, "cli": 2, "ops": 1}
  }
}
```

`stream_targets_required[N]` answers: "if stream N is being bumped, how
many downstream streams does it need to nudge for transitive API safety?"

## Acceptance criteria

- [ ] `python scripts/cross_stream_deps.py` writes
      `.github/cross-stream-dependencies.json` with at least the 19 cross-
      stream edges visible in the current workspace.
- [ ] The `--check` mode exits 0 when the artifact is up-to-date, 4 when it
      drifts (test by hand-editing a crate's `Cargo.toml` to drop an
      internal dep).
- [ ] The cross-stream-bump workflow runs on every PR + push; on PR it
      posts a comment with the edge counts.
- [ ] The artifact is committed alongside workspace metadata so
      release-please can read it offline.

## Follow-on (not this WP, future phases)

- WP-26.b — release-please "post-process" hook that reads the artifact and
  opens follow-up patch-bump PRs against `cli-stream` + `ops-stream`
  whenever `core-stream` lands a non-patch bump.
- WP-26.c — `pt dependency-bump <stream>` subcommand that wraps the
  helper, runs `cargo update -p <broken-dep>`, and re-issues the affected
  stream PRs.
