# Pyright Strict Mode Configuration

**Status**: Active strict mode enabled
**Date**: 2026-02-23
**Baseline Errors**: 373 (reduced from 1132 with pragmatic settings)

## Configuration

The project now has **`pyrightconfig.json`** with strict type checking enabled.

### Key Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| `typeCheckingMode` | `strict` | Enables strictest type checking |
| `pythonVersion` | `3.10` | Match pyproject.toml minimum |
| `reportMissingImports` | true | Catch import issues early |
| `reportUndefinedVariable` | true | Critical: catch undefined names |
| `reportUnusedImport` | true | Clean imports, reduce dependencies |
| `reportUnusedVariable` | true | Catch dead code |
| `reportDeprecated` | true | Update deprecated APIs (e.g., `datetime.utcnow()`) |

### Pragmatic Suppressions (for gradual migration)

The following are disabled to avoid noise during migration:
- `reportMissingParameterType` → Too many functions need annotation
- `reportMissingTypeArgument` → Generic dict/list types pervasive (314 errors)
- `reportUnknownVariableType` → Many third-party types partially unknown
- `reportUnknownMemberType` → LangChain/FastAPI types not fully typed
- `reportUntypedFunctionDecorator` → Decorator libraries not typed (26 errors)
- `reportOptionalMemberAccess` → Would require extensive None checks

**Future Tightening Plan**:
1. Fix undefined variables and import issues (quick wins, 50-100 errors)
2. Fix deprecated API calls (34 datetime.utcnow errors)
3. Add function return type annotations (gradual)
4. Add parameter type annotations (gradual)
5. Enable generic type argument checking (when dict/list are parametrized)

## Running Type Checks

```bash
# Check all types with current config
python -m pyright

# Check single file
python -m pyright 4sgm/backend/models.py

# Show all errors (including suppressed)
python -m pyright --outputjson | jq '.generalDiagnostics'
```

## Current Error Categories (Top 5)

| Type | Count | Fix Strategy |
|------|-------|--------------|
| Deprecated `datetime.utcnow()` | 34 | Replace with `datetime.now(timezone.utc)` |
| Invalid SQLAlchemy conditionals | 15 | Type narrowing for ColumnElement |
| Return type of lambda unknown | 14 | Add explicit return type hints |
| Undefined exceptions | 12 | Add missing imports/definitions |
| Unused imports | Many | Remove or use via TYPE_CHECKING |

## Integration with CI/CD

Add to pre-commit hooks and CI pipeline:

```bash
pyright --outputjson || exit 1
```

Or configure in `pyproject.toml`:

```toml
[tool.pyright]
include = ["4sgm"]
typeCheckingMode = "strict"
```

## Related Files

- **Configuration**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/pyrightconfig.json`
- **Python Version**: Requires Python 3.10+ (from pyproject.toml)
- **Dependencies**: `pip install basedpyright` (optional, preferred over pyright for performance)
