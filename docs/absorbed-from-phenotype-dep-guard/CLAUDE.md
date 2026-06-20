# phenotype-dep-guard

Malicious dependency analysis and supply chain security guard.

## Stack

- Orchestration: Taskfile
- Specs: kitty-specs

## Structure

- `src/` - Python source code
- `tests/` - Test suite
- `schemas/` - JSON schema definitions
- `contracts/` - Interface contracts
- `scripts/` - Automation scripts
- `kitty-specs/` - Specification documents
- `docs/` - Documentation

## Phenotype Org Rules

- UTF-8 encoding only in all text files. No Windows-1252 smart quotes or special characters.
- Worktree discipline: canonical repo stays on `main`; feature work in worktrees.
- CI completeness: fix all CI failures on PRs, including pre-existing ones.
- Never commit agent directories (`.claude/`, `.codex/`, `.gemini/`, `.cursor/`).

## Spec Tracking

Spec work is tracked via AgilePlus: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`
