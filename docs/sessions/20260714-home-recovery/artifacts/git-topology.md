# Git Topology and Recovery Priorities

## Airlock Object Stores

All Airlock repositories below have object stores, but their bare `master` HEAD is not a
usable worktree recovery reference. Worktree Git directories live below the corresponding
bare/common directory as `A/<worktree-id>`. All observed Airlock worktrees are detached.

| Common directory ID | Repository | Worktrees | Canonical bounded match | Safe action |
|---|---|---:|---|---|
| `1112c420a861` | `phenodocs` | 1 | yes | Branch dirty state, review, then compare canonical reachability |
| `164cfe4c6b44` | `thegent` | 1 | yes | Compare clean detached HEAD with canonical refs |
| `1a5895a56a55` | `cliproxyapi-plusplus` | 7 | yes | Branch both critical dirty states before any cleanup |
| `3e17596cb7b9` | `parpour` | 1 | no | Preserve to a named recovery branch and verified remote |
| `656078bd3017` | `civ` | 1 | no | Preserve to a named recovery branch and verified remote |
| `8711057fb661` | `heliosApp` | 3 | yes | Branch critical/high dirty states and reconcile canonical refs |
| `a16844d35f7c` | `trace` | 1 | no | Branch the one-change state and select a verified remote |
| `aa65969b5f61` | `agentapi-plusplus` | 0 | yes | Verify object/ref reachability before considering metadata cleanup |
| `af4fe46f0d25` | `4sgm` | 1 | no | Branch the one-change state and select a verified remote |
| `c6d146851ff4` | `portage` | 0 | yes | Verify object/ref reachability before considering metadata cleanup |
| `fed12af11b16` | `helios-cli` | 1 | yes | Compare clean detached HEAD with canonical refs |

## Airlock Worktrees

Change counts are `tracked/untracked` from the completed read-only topology report.

| Repository | Worktree ID | HEAD | Changes | Priority | Safe action |
|---|---|---|---:|---|---|
| `phenodocs` | `persistent` | `44ec195` | `13/0` | high | Create recovery branch, review and commit intended changes |
| `thegent` | `persistent` | `3156f35` | `0/0` | normal | Compare HEAD reachability; retain until proven redundant |
| `cliproxyapi-plusplus` | `3931d935-a8aa-463c-bc4b-41256085ae65` | `e45f580` | `0/0` | normal | Compare HEAD reachability before cleanup |
| `cliproxyapi-plusplus` | `551affa5-926d-4d14-8dd8-62e4a8a613b5` | `baa4898` | `0/0` | normal | Compare HEAD reachability before cleanup |
| `cliproxyapi-plusplus` | `7faec8a3-7d78-4776-8b0c-0e8cb364e295` | `d053c90` | `2377/103` | **critical** | Freeze; branch; secret/size scan; review and commit in bounded batches |
| `cliproxyapi-plusplus` | `b62b6578-b9a3-4c2c-93b4-2fa2f2989fcc` | `74143b3` | `0/0` | normal | Compare HEAD reachability before cleanup |
| `cliproxyapi-plusplus` | `e450afd1-4973-41ea-9921-65d9ae8ccf2d` | `7da3c91` | `0/0` | normal | Compare HEAD reachability before cleanup |
| `cliproxyapi-plusplus` | `persistent` | `200c201` | `559/0` | **critical** | Freeze; branch; secret/size scan; review and commit in bounded batches |
| `parpour` | `persistent` | `73d7122` | `0/0` | medium | Name branch and establish a trustworthy remote |
| `civ` | `persistent` | `c6a1a42` | `0/0` | medium | Name branch and establish a trustworthy remote |
| `heliosApp` | `2a97c405-f982-4e17-972a-07c34f5c385c` | `5dd7547` | `902/12` | **critical** | Freeze; branch; review and commit before canonical reconciliation |
| `heliosApp` | `5ffb5ebd-13d7-4e47-9aad-1e4d8f0daa9e` | `f224d7a` | `0/0` | normal | Compare HEAD reachability before cleanup |
| `heliosApp` | `persistent` | `e5e101b` | `35/0` | high | Branch, review and commit before canonical reconciliation |
| `trace` | `persistent` | `670dc2e` | `1/0` | medium | Branch and establish a trustworthy remote |
| `4sgm` | `persistent` | `5ae0781` | `1/0` | medium | Branch and establish a trustworthy remote |
| `helios-cli` | `persistent` | `caaa4ea` | `0/0` | normal | Compare HEAD reachability before cleanup |

UUID worktree IDs are recorded in full so recovery commands can be tied back to the exact
Airlock directory and common store.

## Superpowers Worktrees

| Worktree | Common directory | HEAD / branch | Upstream | Changes | Priority and safe action |
|---|---|---|---|---:|---|
| `forgecode/forge-eval-production` | `repos/forgecode/.git` | `9d67435` / `codex/forge-eval-production` | `feat/forge-dev-binary`, `0/0` | `7/61` | **high**: branch already named; review untracked content, commit intended state, then verify remote |
| `melosviz/feat-b10-conductor` | `repos/melosviz/.git` | `8929f42` / `feat/b10-conductor` | `origin/feat/b10-conductor`, ahead 6/behind 1 | `0/0` | **high**: preserve six local commits, fetch, reconcile divergence, push and verify |
| `~/.config/superpowers/worktrees/Tracera-recovery-20260713/tracera-runtime-auth-wbs80-20260714` | `/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera-recovery-20260713/.git` (Git directory: `.git/worktrees/tracera-runtime-auth-wbs80-20260714`) | `7afbf4f` / `codex/…` | none | `0/0` | medium: record full branch, select upstream, push and verify |
| `~/.config/superpowers/worktrees/Tracera/fix-tracera-docker-contract` | `/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera/.git`; missing Git directory `.git/worktrees/fix-tracera-docker-contract` | pointer broken | unknown | unknown | **critical**: inventory files and pointer text before any metadata repair; recover using common objects only after mapping |

The clean Tracera branch name was abbreviated in the source handoff, but its worktree,
Git-directory, and common-directory paths are exact. Expand the branch ref from the
immutable topology ledger before pushing. A broken pointer is not evidence of disposable
content.

## Recovery Order

1. Freeze and branch the three critical Airlock dirty states and inventory the broken
   Tracera pointer.
2. Preserve high-priority dirty/diverged states (`phenodocs`, `heliosApp` persistent,
   `forgecode`, and `melosviz`) to verified remotes.
3. Give clean detached states named branches only where reachability comparison shows the
   commit is not already recoverable from canonical refs.
4. Establish private verified remotes for `parpour`, `civ`, `trace`, and `4sgm`, which had
   no bounded canonical match.
5. Only after independent remote/object verification consider worktree removal or bare
   metadata cleanup. Never move a linked worktree as an ordinary directory.
