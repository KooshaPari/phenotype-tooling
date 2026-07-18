# Home-Level Recovery Session

## Goal

Evaluate every immediate child of `/Users/kooshapari`, recover misplaced source and
worktrees into the `CodeProjects` development environment, and leave every disposition
traceable to a verified remote backup or an explicit keep decision.

## Success Criteria

- All 411 first-level entries have a ledger row and evidence-backed classification.
- No item is deleted, pruned, or overwritten before its preservation gate passes.
- Dirty or detached worktrees are recovered to named branches and verified remotes.
- Misplaced repositories are integrated into their canonical checkout or archived safely.
- Loose source, documents, and dumps are assigned to a repository, private quarantine, or
  explicit home-level keep category.
- Final verification proves that backed-up content is reachable from a remote reference.

## Operating Decisions

- Use `phenotype-org-audits` as the audit and provenance spine.
- Use `KooshaPari/home-recovery-2026-07` as a private fallback remote only when no
  trustworthy upstream exists.
- Prefer existing upstream repositories over the quarantine remote.
- Treat `~/.airlock` and `~/.config/superpowers/worktrees` as P0 preservation zones.
- Keep the audit scope to immediate children of `~`; inspect descendants only to determine
  the first-level entry's identity, Git topology, and safe disposition.

## Links

- Audit branch: `audit/home-recovery-2026-07`
- Private fallback: `https://github.com/KooshaPari/home-recovery-2026-07`

