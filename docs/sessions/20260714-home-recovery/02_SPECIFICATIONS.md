# Specifications

## Scope

The unit of evaluation is every immediate child of `/Users/kooshapari`. Descendant scans
are bounded to evidence needed to classify the owning first-level entry. System-managed
directories such as `Library`, application configuration, caches, credentials, and shell
state are evaluated but are not automatically relocation candidates.

## Ledger Contract

Each entry must record:

1. exact path and stable escaped display name;
2. file type, size class, modification time, and content-risk class;
3. purpose and ownership category;
4. Git repository/worktree identity where applicable;
5. dirty, untracked, detached, upstream, ahead, and behind state;
6. canonical destination or keep-in-place reason;
7. backup target and verification evidence;
8. disposition state and rollback path.

## Disposition States

- `KEEP_HOME`: correct system, user, configuration, or application state.
- `KEEP_REVIEW`: correct location is plausible but requires owner review.
- `REPO_INTEGRATE`: content belongs in an existing repository.
- `REPO_RELOCATE`: standalone repository belongs under `CodeProjects`.
- `WORKTREE_RECOVER`: dirty, detached, broken, or ahead worktree needs preservation.
- `QUARANTINE_PRIVATE`: no trustworthy upstream; preserve in the private fallback.
- `ARCHIVE_EXTERNAL`: binary, secret-bearing, or oversized content needs encrypted or
  non-Git remote storage.
- `REDUNDANT_VERIFIED`: source is redundant only after remote and destination verification.

## Preservation Gates

No destructive disposition is allowed until all applicable gates pass:

1. identity and ownership established;
2. secret and large-file risk assessed;
3. destination selected without collision;
4. content committed or archived with a stable identifier;
5. remote copy verified independently;
6. canonical checkout or archive restored and checked;
7. source-to-destination manifest recorded;
8. explicit deletion batch approved.

## Assumptions, Risks, and Uncertainties

| Item | Type | Mitigation |
|---|---|---|
| Hidden directories may contain credentials | Risk | Never print values; classify by metadata; exclude from Git |
| Detached worktrees may share object stores | Risk | Record common Git directory before any move |
| Local upstream refs may be stale | Uncertainty | Fetch only during repo-specific recovery, then compare |
| Large worktrees may exceed Git hosting limits | Risk | Use Git LFS or encrypted external archive after inspection |
| A visible duplicate may contain unique commits | Risk | Compare commits and trees, not directory names |
| Malformed filenames may be shell artifacts | Assumption | Preserve exact bytes and hash before disposition |

