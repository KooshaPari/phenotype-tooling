# phenotype-py-extras — AGENTS.md

## Project Overview

phenotype-py-extras is part of the Phenotype polyrepo. It provides shared Python infrastructure
(types, ports, adapters) consumed by the rest of the org.

## Stack

- Language: Python 3.14+
- Build system: hatchling
- Type-checker: pyright (strict)
- Linter: ruff
- Tests: pytest + pytest-asyncio + respx (for httpx mocks)

## Key Commands

```bash
# Install dev deps
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check src tests
uv run ruff format --check src tests

# Type-check
uv run pyright

# Audit dependencies
uv run pip-audit

# Build
uv build
```

## Notes

- Per-repo CI is the same as the other Phenotype Python repos: ruff, pyright,
  pytest, pip-audit, deptry, vulture.
- This repo follows the standard Phenotype-org `.github/` shape (dependabot +
  release-attestation + scorecard).
