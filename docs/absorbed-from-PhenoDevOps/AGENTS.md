# AGENTS.md — PhenoDevOps

**Status:** DRAINING (per `plans/2026-06-18-devhex-port-v1.md` and the
`PhenoDevOps` × `DevHex` overlap audit, 2026-06-17).

This file replaces the prior triple-merge-corrupt `AGENTS.md` (which had
unresolved `<<<<<<< HEAD` / `=======` / `>>>>>>> origin/main` markers
interleaving content from the `repos/` shelf, `phenotype-infrakit`, and
`PhenoDevOps` itself). All non-`PhenoDevOps`-specific content has been
removed. See git history (`git log -p -- AGENTS.md`) for the previous
content if you need to recover anything.

---

## Identity

`PhenoDevOps` is the **DevOps and infrastructure automation platform** for
the Phenotype ecosystem (per `PhenoDevOps/CHARTER.md:29`).

Its sole genuine payload is `agent-devops-setups/` (Python policy
federation + shell scripts + VitePress docs) — everything else in this
repo (the 60+ Rust crates under `crates/`, the `agileplus-*` workspace,
`bifrost-routing*`, `forgecode-*`, `phenotype-router-monitor`) is being
migrated to canonical homes in a multi-stage drain:

| Sub-tree | Target | Stage |
|---|---|---|
| `agent-devops-setups/` (38 files) | `phenotype-ops` | **Stage 1** — in flight, PR #TBD |
| `crates/agileplus-*` (25 crates) | `AgilePlus` | Stage 2 |
| `crates/phenotype-*` duplicates (~28 crates) | `HexaKit` | Stage 3 |
| `crates/bifrost-routing*/` (no `Cargo.toml`) | (delete) | Stage 4 |
| `crates/forgecode-core/`, `phenotype-router-monitor/`, `forgecode-fork/`, `agileplus/`, `agileplus-mcp/` | (delete) | Stage 4 |
| `crates/phenotype-retry/`, `crates/phenotype-time/` | `HexaKit` (decision pending) | Stage 3 or 4 |
| This repo | **archived** per ADR-029 | Stage 5 |

After Stage 5, this repo is archived (read-only marker per ADR-029);
no active maintenance happens here.

---

## Parent governance

This repo lives inside the `repos/` monorepo. The canonical
monorepo-wide `AGENTS.md` is at `../AGENTS.md` (one level up from this
directory). All shelf-level rules from there apply here.

**Specific overrides / additions for `PhenoDevOps` work:**

- The git remote for this repo is `git@github.com:KooshaPari/PhenoDevOps.git`.
  The remote was previously mislabelled as `phenotype-infrakit` in
  `Cargo.toml:7`; that is being fixed as part of Stage 1.
- Active work happens on branches named
  `chore/<req-id>-<slug>-<date>` or `feat/<req-id>-<slug>-<date>`.
  The pre-drain WIP snapshot branch is `wip/2026-06-17-pre-drain-snapshot`
  (pushed to remote).
- No new content should be added to this repo except as part of an
  explicit migration PR. If you need to add something, file an ADR
  first in `docs/adr/2026-06-18/` and tag `governance`.

---

## Quick reference

```bash
# Stage 1 PR: agent-devops-setups -> phenotype-ops
cd ../phenotype-ops
git switch -c feat/absorb-pheno-devops-setups-2026-06-18
# (copy + adjust) ../PhenoDevOps/agent-devops-setups/  ->  agent-devops-setups/
# open PR: gh pr create --repo KooshaPari/phenotype-ops

# Stage 2-4 PRs: crate drain to AgilePlus + HexaKit
# Stage 5: gh repo archive KooshaPari/PhenoDevOps
```

---

## See also

- `CHARTER.md` — official charter (the only authoritative doc on what
  `PhenoDevOps` is meant to be).
- `README.md` — currently mislabelled as a "repos shelf" README; this
  will be fixed in Stage 5 (or replaced with a deprecation pointer).
- `Cargo.toml` — workspace manifest; the `[workspace.dependencies]`
  block has drift that needs cleanup before Stage 3.
- `docs/adr/` — currently empty; new ADRs for the drain go here.
- Parent monorepo: `../AGENTS.md` and `../STATUS.md`.
