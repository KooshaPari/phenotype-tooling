# Absorbed from PhenoRMCP (post-deletion)

**Source:** `KooshaPari/PhenoRMCP` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-PhenoRMCP/`

## Status

Source repository was archived and then deleted on GitHub 2026-06-21.
No local clone was available at the time of deletion.

## Note on absorption

This absorption manifest was authored AFTER the source repo was deleted.
The full source content is therefore not preserved in this collection.

For source content recovery:
- The GitHub tombstone is recoverable via the GitHub API within 90 days of deletion
- No local clone was available; the source content is therefore unrecoverable from local disk

## Why this happened

The repo was missed in the L5-113 absorption wave on 2026-06-20 because the
`gh repo list` query used a stale isArchived cache. The next query run on
2026-06-21 revealed the archived repos that were not yet absorbed, and they
were deleted directly without preserving source content first.

This is a process gap: deletion-justification was not documented for these
repos. This manifest is the minimum retroactive record.
