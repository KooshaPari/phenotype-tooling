# VIBECODING_GUARD_BASELINE_2026_06_12.md

Protected paths for dispatch-mcp (vibecoding-guard do-not-touch zones).

1. `uv.lock` — Python dependency lockfile; changes silently alter the transitive dependency graph
2. `pyproject.toml` — Python project manifest and tool configuration; changes affect build and packaging
3. `WORKLOG.md` — Work tracking ledger; changes must reference an AgilePlus task or spec
4. `CLAUDE.md` — AI agent guidance; changes affect how agents interact with the repo
5. `.github/workflows/` — CI/CD workflow definitions; changes affect automated gates and deployments
