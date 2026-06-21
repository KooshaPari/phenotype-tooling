# phenoXdd — Agent Instructions

See [CLAUDE.md](./CLAUDE.md) for project-specific guidance.
See `~/.claude/CLAUDE.md` for global agent rules and Phenotype org conventions.

## Quick Reference

- **Collection:** Paginary (consolidated docs)
- **Status:** ACTIVE
- **Worktree pattern:** `repos/phenoXdd-wtrees/<topic>/`
- **Language:** Documentation-only reference
- **Quality gates:** markdown lint, link checks, governance checks

## Mandatory checks before PR

- All TODO/FIXME markers reviewed
- `README.md` and `SPECS_INDEX.md` remain in sync
- `docs/` links are valid and relative paths resolve
- `FUNCTIONAL_REQUIREMENTS.md` statuses align with `tests/` evidence
- No runtime project manifests are added unless explicitly approved by architecture owners

## Review Checklist

1. Validate that PRD constraints are respected
2. Verify no broken internal links
3. Verify any plan/scope changes are reflected in `SPECS_INDEX.md`
4. Confirm workflow files avoid broken interpolation syntax

## Completion State

This repository is currently considered a documentation compendium and should not ship runtime artifacts.
