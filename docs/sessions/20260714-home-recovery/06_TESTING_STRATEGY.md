# Testing Strategy

## Inventory Tests

- Compare null-delimited first-level enumeration count against the ledger count.
- Ensure every absolute path is unique and round-trips without shell interpretation.
- Verify hidden and visible totals remain 335 and 76 for the baseline snapshot.

## Git Tests

- Validate `git rev-parse --git-dir` and `--git-common-dir` for every candidate.
- Record `git status --porcelain=v2 --branch` without mutating the index.
- Confirm recovery branches contain the expected source HEAD and captured changes.
- Confirm pushed recovery commits with `git ls-remote` or the GitHub API.

## Content Safety Tests

- Run secret detection before staging any recovered source.
- Detect files above Git and GitHub size thresholds before commit creation.
- Compare hashes or Git tree objects between source and restored destination.
- Restore a sample external archive before marking it verified.

## Relocation Acceptance Tests

- Destination exists and has the expected content hash or Git tree.
- Canonical repository remains valid and its worktree list has no broken new entries.
- Source is retained until a separate cleanup gate is approved.
- Final ledger contains no `UNKNOWN` disposition or unverified destructive action.

