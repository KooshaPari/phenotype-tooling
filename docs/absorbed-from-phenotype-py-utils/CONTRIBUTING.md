# Contributing

Thanks for your interest in `phenotype-py-utils`! This is a small, focused
library. The contribution surface is intentionally narrow.

## Scope

This package is for **utility functions used across 3+ Phenotype Python
repos**. If your function is single-use, it belongs in the consuming
repo, not here. When in doubt, open a draft PR and ask.

## Pull-request checklist

- [ ] New functions are exported from `phenotype_py_utils/__init__.py`.
- [ ] Each public function has a docstring (Args / Returns / Raises).
- [ ] Tests added in `tests/` (one per behaviour, not per function).
- [ ] `pytest` is green; coverage stays at 100% for the new lines.
- [ ] `mypy src` is clean (`strict = true`).
- [ ] `ruff check src tests` is clean.
- [ ] `CHANGELOG.md` updated under the "Unreleased" section.

## Local dev

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
mypy src
ruff check src tests
```

## Versioning

`phenotype-py-utils` follows [SemVer](https://semver.org/). Since this is
pre-1.0, breaking changes bump the minor version.

## Release process

1. Bump `__version__` in `src/phenotype_py_utils/__init__.py` and
   `version` in `pyproject.toml`.
2. Move the "Unreleased" entries in `CHANGELOG.md` under a new version
   heading with the date.
3. Commit, tag (`git tag -a v0.X.Y -m "..."`), push.
4. The CI workflow builds and publishes to PyPI (configured separately).
