<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/phenotype-py-utils/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/phenotype-py-utils?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/phenotype-py-utils?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->
# phenotype-py-utils

[![Python](https://img.shields.io/pypi/pyversions/phenotype-py-utils)](https://pypi.org/project/phenotype-py-utils/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Typed](https://img.shields.io/badge/typing-typed-blue.svg)](https://peps.python.org/pep-0561/)

Shared Python utility library for the Phenotype org.

This package consolidates a small set of utility functions that are
commonly copied across Python projects in the Phenotype org. By depending
on this library, downstream repos get a single canonical implementation
that is tested, typed, and follows the org's quality bar
(`mypy --strict`, `ruff`, `pytest` with coverage).

## Features

- **`load_config`** — load YAML / TOML / JSON config from a path with env-var
  override (`PHENOTYPE_<KEY>__<SUBKEY>` style).
- **`setup_logging`** — configure stdlib logging with sensible defaults, plus
  an optional JSON formatter for OTel / log aggregators.
- **`parse_args`** — parse CLI args into a typed `dataclass` return value.
- **`iso_now`** — get the current UTC time as an ISO 8601 string with a `Z` suffix.
- **`truncate`** — truncate a string with a configurable suffix.

All public symbols are re-exported from the top-level package
(`from phenotype_py_utils import load_config, …`).

## Installation

```bash
pip install phenotype-py-utils
```

With the optional TOML support for Python 3.10 (3.11+ uses the stdlib
`tomllib` automatically):

```bash
pip install phenotype-py-utils[toml]
```

For development (test, lint, type-check):

```bash
pip install "phenotype-py-utils[dev]"
```

## Quick start

```python
from phenotype_py_utils import (
    load_config,
    setup_logging,
    parse_args,
    iso_now,
    truncate,
)

# 1. Logging — one-liner setup with optional JSON output
setup_logging("INFO", json_output=True)

# 2. Config — load + env-var override (PHENOTYPE_LOG__LEVEL=DEBUG)
cfg = load_config("config.yaml")
print(cfg["log"]["level"])

# 3. CLI — dataclass → argparse
from dataclasses import dataclass

@dataclass
class MyTool:
    """A phenotype-style CLI tool."""
    path: str
    verbose: bool = False

args = parse_args(MyTool)
print(args)

# 4. Timestamps — always UTC, Z-suffixed
print(iso_now())  # '2026-06-12T01:23:45.678901Z'

# 5. Strings
print(truncate("a very long commit message …", max_len=20))
# 'a very long commit...'
```

## API reference

### `load_config`

```python
def load_config(
    path: str | Path,
    *,
    env_override: bool = True,
    env_prefix: str = "PHENOTYPE_",
) -> dict[str, Any]
```

Loads a config file. The format is auto-detected from the extension
(`.yaml`, `.yml`, `.toml`, `.json`). When `env_override` is enabled (the
default), any env var named `<PREFIX><KEY>__<SUBKEY>` (double underscore
for nesting) overrides the loaded config as a string.

Example: `PHENOTYPE_LOG__LEVEL=DEBUG` overrides `log.level`.

Raises `ConfigError` on missing file, parse error, or non-mapping root.

### `setup_logging`

```python
def setup_logging(
    level: str = "INFO",
    *,
    json_output: bool = False,
    format: str = DEFAULT_FORMAT,
    stream: Any = None,
) -> None
```

Configures the root logger with a single handler. Idempotent — clears
existing handlers before adding the new one. When `json_output=True`,
records are emitted as single-line JSON with `ts`, `level`, `logger`,
`msg`, and (when present) `exc`.

### `parse_args`

```python
def parse_args(cls: Type[T], argv: Sequence[str] | None = None) -> T
```

Builds an `argparse.ArgumentParser` from a `@dataclass` and returns an
instance of `cls`. Field type is used for `type=` (or
`argparse.BooleanOptionalAction` for `bool` fields). Field default is
used for `default=`, and `required=True` is set when the field has no
default.

### `iso_now` / `from_unix`

```python
def iso_now() -> str       # '2026-06-12T01:23:45.678901Z'
def from_unix(ts: float) -> str
```

Both return UTC, ISO 8601 with a `Z` suffix. The `Z` form is friendlier
for browsers, JSON, and OpenTelemetry.

### `truncate` / `slugify`

```python
def truncate(s: str, max_len: int = 80, suffix: str = "...") -> str
def slugify(s: str) -> str  # 'untitled' for empty/all-special input
```

`truncate` is character-based (not byte-based) and raises `ValueError`
if `max_len < len(suffix)`.

## Development

```bash
git clone git@github.com:KooshaPari/phenotype-py-utils.git
cd phenotype-py-utils
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest          # 59 tests, with coverage
mypy src        # strict
ruff check src tests
```

## License

MIT — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
