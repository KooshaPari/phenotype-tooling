# DAG and Work Breakdown

## Dependency Graph

```text
A. Inventory 411 entries
├── B. Classify system/config/secret state
├── C. Map Git repositories and common directories
└── D. Identify loose code, docs, dumps, and malformed entries
    └── E. Select canonical destination
        ├── F. Existing-upstream recovery
        ├── G. Private-quarantine recovery
        └── H. Encrypted external archive
            └── I. Verify remote reachability and restored content
                └── J. Relocate into CodeProjects or canonical repo
                    └── K. Approve and remove verified redundant sources
```

## Work Packages

| WP | Work | Dependency | Completion Evidence |
|---|---|---|---|
| WP1 | First-level ledger | none | 411 unique paths, no omissions |
| WP2 | Git/worktree topology | WP1 | common dirs, HEADs, dirty counts, remotes |
| WP3 | P0 worktree preservation | WP2 | named remote refs for every recovered state |
| WP4 | Visible loose-artifact integration | WP1 | destination and backup for each candidate |
| WP5 | Hidden configuration decisions | WP1 | keep/recover decision for all 335 entries |
| WP6 | Physical relocation | WP3-WP5 | destination checks and manifest updates |
| WP7 | Redundancy cleanup | WP6 | independent backup proof and approval |
| WP8 | Final audit closeout | WP7 | zero unclassified entries and remote evidence |

## Critical Path

`WP1 → WP2 → WP3 → WP6 → WP7 → WP8`

P0 priority is assigned to dirty detached worktrees, broken Git pointers, locally ahead
branches, and any artifact with no second copy.

