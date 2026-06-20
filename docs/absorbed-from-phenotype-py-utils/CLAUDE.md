# phenotype-py-utils — CLAUDE.md

## Quick Reference

| Task | Command |
|------|---------|
| Install | `uv sync --extra dev` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check src tests` |
| Format | `uv run ruff format src tests` |
| Type-check | `uv run pyright` |
| Audit | `uv run pip-audit` |
| Build | `uv build` |

## Conventions

- Type hints required on all public functions (pyright strict)
- Tests live in `tests/`, mirror the source tree
- 100% coverage expected on `src/`
- Use `from __future__ import annotations` for PEP-563 forward refs
- Conventional commits (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`)
- No commits to `main` — use feature branches + PR
