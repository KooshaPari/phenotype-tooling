<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/phenotype-py-extras/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/phenotype-py-extras?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/phenotype-py-extras?style=flat-square)
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
# phenotype-py-extras

Shared Python extras for the Phenotype ecosystem.

A single zero-dependency package that downstream projects can depend on instead
of duplicating common dep lists. Optional extras groups are re-exported lazily
through PEP 562 `__getattr__`, so importing `phenotype_py_extras` never pulls
in transitive dependencies.

## Install

```bash
# Pick the groups you need
pip install phenotype-py-extras[cli]
pip install phenotype-py-extras[mcp]
pip install phenotype-py-extras[web]
pip install phenotype-py-extras[testing]
pip install phenotype-py-extras[testing-quality]
pip install phenotype-py-extras[observability]

# Or everything at once
pip install phenotype-py-extras[all]
```

## Usage

```python
# The package core has zero runtime deps; this always works.
import phenotype_py_extras
print(phenotype_py_extras.__version__)

# Submodules are also safe to import; only attribute access is lazy.
from phenotype_py_extras import cli, mcp, web, testing

# Accessing an extras attribute triggers the underlying import.
# If the matching extras group is not installed, you get ImportError on access.
from phenotype_py_extras.cli import click
from phenotype_py_extras.mcp import fastmcp, pydantic
from phenotype_py_extras.web import fastapi
from phenotype_py_extras.testing import pytest
```

## Extras groups

| Group              | Libraries                                                       |
|--------------------|-----------------------------------------------------------------|
| `cli`              | click, rich, typer, pydantic                                    |
| `mcp`              | fastmcp, pydantic, pydantic-settings, httpx                     |
| `web`              | fastapi, uvicorn, pydantic, pydantic-settings                   |
| `testing`          | pytest, pytest-asyncio, pytest-cov                              |
| `testing-quality`  | testing + coverage, mypy                                        |
| `observability`    | structlog, loguru                                               |
| `all`              | everything above                                                |
