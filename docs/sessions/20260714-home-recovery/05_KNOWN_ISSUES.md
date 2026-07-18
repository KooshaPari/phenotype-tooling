# Known Issues

| Severity | Issue | Current Control |
|---|---|---|
| P0 | `~/.airlock` has 11 bare/common stores and 16 detached worktrees | Frozen from cleanup and relocation; topology captured in artifact |
| P0 | Airlock critical states contain `2377/103`, `559/0`, and `902/12` tracked/untracked changes | Branch, scan, review, and commit before content handling |
| P0 | Tracera superpowers worktree has a broken Git pointer while common objects exist | Inventory files and pointer before any metadata repair |
| P0 | melosviz worktree is ahead 6 and behind 1 | Preserve local commits before reconciliation |
| P1 | Live inventory is 408 versus initial 411, with one discrepancy still unidentified | Preserve both snapshots; do not infer the third identity |
| P1 | `~/CLIProxyAPI` disappeared externally | Unique commit independently verified on remote recovery branch |
| P1 | `~/router-rb-2c` disappeared externally and exact baseline HEAD was not captured | Retain clean/tracking baseline fact; verify canonical remote before disposition closure |
| P1 | Home contains malformed and zero-byte filename artifacts | Hash and preserve names before disposition |
| P1 | Loose dumps may contain sensitive data | Metadata-first inspection; no public Git |
| P1 | Historical audit files contain credential-shaped text | Never copy raw audit content into public outputs |
| P1 | `parpour`, `civ`, `trace`, and `4sgm` have no bounded canonical matches | Create named recovery branches and choose verified private remotes |
| P2 | The clean Tracera branch ref was abbreviated in the synthesis handoff | Expand the branch ref from the immutable topology ledger before pushing |

No workaround authorizes deletion. Issues leave this document only after verification evidence
is recorded in the ledger.
