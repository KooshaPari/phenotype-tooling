# 4sgm Governance Summary

> **Status**: Production project.

## Project Classification

- **Type**: Production API service
- **Language**: Python
- **Package Manager**: uv
- **Linter**: ruff

## Architecture

```
4sgm/
├── 4sgm/           # Core application
├── backend/        # FastAPI backend
├── cli.py          # CLI interface
└── tests/          # Test suite
```

## Quality Gates

| Gate | Command |
|------|---------|
| Lint | `task lint` |
| Format | `task format` |
| Test | `task test` |
| Typecheck | `task typecheck` |
| All | `task check` |

## Standards

- Use ruff for linting/formatting
- Type hints required for new code
- pytest for testing
- SQLAlchemy 2.0 patterns

## References

- Taskfile: See `Taskfile.yml`
- Config: `pyproject.toml`
