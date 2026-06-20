# Changelog

All notable changes to `phenotype-py-utils` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-20

### Added
- `extras` subpackage: optional dependency groups absorbed from `phenotype-py-extras`.
- `extras.cli` — lazy re-exports of click, rich, typer, pydantic.
- `extras.mcp` — lazy re-exports of fastmcp, pydantic, pydantic-settings, httpx.
- `extras.web` — lazy re-exports of fastapi, uvicorn, pydantic, pydantic-settings.
- `extras.testing` — lazy re-exports of pytest, pytest-asyncio, pytest-cov.
- `extras.llms_txt` — llms.txt renderer (absorbed from phenotype-py-extras).

### Changed
- Version bumped to 0.2.0.

## [0.1.0] - 2026-06-12

### Added
- `load_config(path, *, env_override=True, env_prefix="PHENOTYPE_")` — load
  YAML / TOML / JSON config from a path with env-var override using
  `<PREFIX><KEY>__<SUBKEY>` style. `ConfigError` on missing / unparseable file.
- `setup_logging(level="INFO", *, json_output=False, format=DEFAULT_FORMAT, stream=None)` —
  stdlib logging wrapper that clears existing handlers and adds a single
  one. Optional JSON formatter for OTel / log aggregators.
- `parse_args(cls, argv=None)` — typed CLI argument parser that builds an
  `argparse.ArgumentParser` from a `@dataclass` and returns a populated
  instance. `bool` fields use `argparse.BooleanOptionalAction`.
- `iso_now() -> str` — current UTC time as an ISO 8601 string with `Z` suffix.
- `from_unix(ts: float) -> str` — convert a Unix timestamp to the same format.
- `truncate(s, max_len=80, suffix="...")` — character-based string truncation.
- `slugify(s) -> str` — URL-safe lowercase slug (returns `"untitled"` for
  empty / all-special input).
- `JsonFormatter` — `logging.Formatter` subclass that emits single-line JSON.
- `py.typed` marker (PEP 561).
- 58 tests, 100% coverage, `mypy --strict` clean, `ruff` clean.
