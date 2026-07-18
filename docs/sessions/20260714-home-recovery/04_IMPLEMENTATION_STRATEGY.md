# Implementation Strategy

## Chosen Approach

Use a manifest-first, upstream-first, private-fallback recovery pipeline.

1. Generate a deterministic first-level ledger without reading secret contents.
2. Enrich candidate rows with bounded Git and file-type evidence.
3. Freeze P0 paths from cleanup and record their common Git object directories.
4. Recover unique Git state into named branches in the correct upstream repository.
5. Use the private quarantine only for orphaned source with no safe canonical upstream.
6. Use encrypted external storage rather than Git for secrets or oversized binary state.
7. Relocate only after backup verification and destination collision checks.
8. Delete only in a separately approved batch with a rollback manifest.

## Recovery Branch Convention

`recovery/2026-07-14/<source-slug>/<short-head>`

Each recovery commit must identify the original absolute path, original HEAD, common Git
directory, dirty/untracked counts, and the ledger row identifier. Secret scans run before
commit creation.

## Remote Verification

- Existing upstream: confirm the recovery commit appears under a remote branch reference.
- Private quarantine: confirm repository visibility is private and the exact object is
  reachable from a pushed reference.
- External archive: record checksum, encryption method identifier, destination, and restore
  verification without recording credentials.

## Relocation Rules

- Never move a linked worktree before its common directory and branch are recovered.
- Never overwrite an existing `CodeProjects` path.
- Prefer canonical repository worktrees over duplicate standalone clones.
- Preserve timestamps and hashes in the ledger even when Git records the logical content.
- Keep macOS system folders and active application state in their supported locations.

