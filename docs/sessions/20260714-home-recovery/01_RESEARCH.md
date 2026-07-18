# Research

## Home Inventory Baseline and Live Drift

- Initial snapshot: 411 immediate entries (335 hidden, 76 visible)
- Reconciled live inventory: 408 immediate entries (335 hidden, 73 visible)
- Exact baseline/current parsing proves that `~/CLIProxyAPI` and `~/router-rb-2c` are now
  absent; the third entry in the count difference remains unresolved.
- Directories: 286
- Regular files: 123
- Symbolic links: 1
- Zero-byte top-level files: 8
- Baseline direct home-level Git repositories: `.oh-my-zsh`, `CLIProxyAPI`, and
  `router-rb-2c`; the latter two are now externally missing.

The live disposition arithmetic is
`239 KEEP_HOME + 120 KEEP_REVIEW + 10 REPO_INTEGRATE + 2 REPO_RELOCATE +`
`1 WORKTREE_RECOVER + 15 QUARANTINE_PRIVATE + 21 ARCHIVE_EXTERNAL = 408`.
The full reconciled groups are recorded in `artifacts/home-classification.md`.

## Critical Findings

- `~/.airlock` is approximately 30.45 GiB and contains 20 detached Git worktrees.
- Nine observed `~/.airlock` worktrees are dirty, including high-change-count states.
- `~/.config/superpowers/worktrees` contains four additional worktrees.
- One superpowers worktree has a stale or broken Git pointer.
- One melosviz worktree is locally six commits ahead and one commit behind its upstream.
- The missing `~/CLIProxyAPI` unique commit is not in the inspected canonical or Airlock
  object stores, but `git ls-remote` verifies full commit
  `f5cbb192222dab78b710a8b94188fbf456232830` at
  `refs/heads/koosha/security-and-test-coverage-policy` in
  `KooshaPari/cliproxyapi-plusplus`.
- The missing `~/router-rb-2c` was clean and tracking `origin/main` for
  `KooshaPari/phenotype-router` at baseline; its exact prior HEAD was not captured.
- Airlock contains 11 bare/common object stores and 16 detached worktrees. Three dirty
  states are critical: `cliproxyapi-plusplus` at `d053c90` (`2377/103`) and `200c201`
  (`559/0`), plus `heliosApp` at `5dd7547` (`902/12`).
- Canonical matches were bounded for `agentapi-plusplus`, `cliproxyapi-plusplus`,
  `helios-cli`, `heliosApp`, `phenodocs`, `portage`, and `thegent`; no bounded matches were
  found for `parpour`, `civ`, `trace`, or `4sgm`.
- The four superpowers worktrees include dirty `forgecode` (`7/61`), diverged `melosviz`
  (ahead 6/behind 1), a clean no-upstream Tracera recovery branch, and a broken Tracera
  pointer whose common objects still exist.

Exact topology and safe actions are recorded in `artifacts/git-topology.md`.

## Repository Precedent

- `phenotype-org-audits` is the existing organization-wide inventory and audit spine.
- Existing AgilePlus worktree audits establish that orphaned worktrees must be inventoried
  and recovered before references are removed.
- The current task is broader than those audits because it includes hidden worktree stores,
  loose artifacts, and misplaced home-level checkouts.

## Safety Research

- Git worktrees must be mapped through both `--git-dir` and `--git-common-dir`; a `.git`
  file can be a live worktree pointer rather than an independent repository.
- Detached worktree content must be placed on a named recovery branch before relocation.
- Secret-bearing files and large binary state must not be pushed to a normal source branch.
- A remote URL alone is not backup proof; the target commit must be present in `ls-remote`
  output or otherwise verified through the hosting API.
