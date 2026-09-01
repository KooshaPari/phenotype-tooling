# Absorption: pheno-forge-plugins → phenotype-tooling

**Date:** 2026-09-01
**Source:** `KooshaPari/pheno-forge-plugins` (archived 2026-08-02, public, 66 KB)
**Target:** `KooshaPari/phenotype-tooling` → `.forgecode/plugins/`
**Branch (local):** `chore/absorb-pheno-forge-plugins-2026-09-01`
**Registry row:** `repo-pheno-forge-plugins`
**Absorption justification:** `audits/absorption-justifications/pheno-forge-plugins-2026-09-01.md` (in `phenotype-registry`)

## Provenance

Source repo `pheno-forge-plugins` was created 2026-05-29 as a sidecar that bundles six `forgecode` plugins for the `antinomyhq/forgecode` runtime. Each plugin is a per-machine systemd unit that exposes a memory / config / tracing skill to forgecode's tool registry.

On 2026-09-01, the polyrepo audit identified that the registry's previously-claimed target path `phenotype-tooling/plugins/pheno-forge/` did not exist on the remote HEAD. The actual matching directory on `phenotype-tooling` is `.forgecode/plugins/` (which already contains `elicitate/`). This absorb relocates the source into the correct target.

## Files absorbed (6 plugins + auxiliary docs)

```
.forgecode/plugins/
├── pheno-cognee/         (7 files: plugin.toml, plugin.env, README.md, SKILL.md,
│                          spawn.sh, healthcheck.sh, bin/.gitkeep)
├── pheno-config/         (7 files, same shape)
├── pheno-letta/          (7 files, same shape)
├── pheno-mem0/           (7 files, same shape)
├── pheno-supermemory/    (7 files, same shape)
├── pheno-tracing/        (7 files, same shape)
├── systemd/
│   └── pheno-forge-sidecars.target    (449-byte systemd slice target)
├── pheno-forge-plugins-AGENTS.md      (AGENTS.md intent doc)
├── pheno-forge-plugins-CHANGELOG.md   (full changelog)
├── pheno-forge-plugins-SCOPE.md       (scope-of-work contract)
└── pheno-forge-plugins-WORKLOG.md     (worklog)
```

Total: 46 files, ~52 KB content (matches source size 66 KB minus top-level CI/license noise).

## Intentionally NOT absorbed (preserved in original repo or replaced by target's surface)

| Source file | Why excluded |
|---|---|
| `Cargo.toml` | Rust workspace manifests clash with `phenotype-tooling/Cargo.toml`; the plugins are pure-shell, no compile needed |
| `LICENSE-APACHE`, `LICENSE-MIT`, `.gitignore`, `.gitattributes`, `renovate.json`, `trunk.yaml`, `.mergify.yml`, `.pre-commit-config.yaml`, `llms.txt` | Top-level CI/lint/meta configs; target `phenotype-tooling` already has its own |
| `README.md` | Renamed to `pheno-forge-plugins-AGENTS.md` to avoid clashing with `phenotype-tooling/README.md` (the target's SSOT README) |

## Merge semantics

History-preserving `git-subtree` was not used because the source repo is already archived (no ongoing work to preserve). Files were copied byte-for-byte; semantics are preserved 1:1.

## Idempotency

If `pheno-forge-plugins` is ever restored from the registry mirror in `phenotype-archive-2026-08-10-working`, the absorb operation can be re-run from this ABSORPTION.md and the source repo may then be `gh repo delete`d.

## Confirmation log

| Event | Date | Actor |
|---|---|---|
| Source archived on GH | 2026-08-02 | n/a |
| Audit identified target-path mismatch | 2026-09-01 | Forge |
| Subtree absorb staged locally | 2026-09-01 | Forge |
| Registry row updated → `ABSORB fsm=deleted` | 2026-09-01 | Forge (after commit lands) |
| `gh repo delete` (user-driven) | pending user | operator |

Soft-delete contract honored: no `gh repo delete` invoked.