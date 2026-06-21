<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/QuadSGM/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/QuadSGM?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/QuadSGM?style=flat-square)
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
# QuadSGM

Structured governance framework for Phenotype providing standards, metrics, and automation for code quality, documentation, and policy enforcement across the ecosystem.

## Overview

QuadSGM (Quad Structured Governance Model) is a comprehensive project template and automation framework that establishes consistent standards for Python projects in the Phenotype ecosystem. It includes task runners, documentation scaffolding, CI/CD integration, and policy validation to ensure all projects meet governance requirements.

## Technology Stack

- **Language**: Python 3.10+
- **Package Manager**: uv
- **Task Runner**: Task
- **Documentation**: VitePress, Markdown
- **CI/CD**: GitHub Actions
- **Quality Gates**: Ruff, Mypy, Vale
- **Build**: Hatch

## Key Features

- Standardized Python project layout
- Automated quality checks (lint, format, type, docs)
- Task-driven development workflow
- Governance policy validation
- Test coverage tracking
- Documentation generation
- Automated CI/CD workflows
- Specs and tracker integration
- Dependency management

## Quick Start

```bash
# Clone repository
git clone https://github.com/KooshaPari/QuadSGM.git
cd QuadSGM

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run quality checks
task quality

# Run tests
task test

# Build documentation
task docs:build

# Run all governance validation
task validate
```

## Project Structure

```
QuadSGM/
├── quadsgm/                    # Core package
│   ├── framework/              # Governance framework
│   │   ├── quality.py          # Quality gates
│   │   ├── specs.py            # Specification validation
│   │   └── policy.py           # Policy enforcement
│   ├── cli/                    # CLI tools
│   │   ├── validate.py         # Validation commands
│   │   ├── init.py             # Project initialization
│   │   └── sync.py             # Sync governance
│   └── __init__.py
├── docs/                       # Documentation
│   ├── governance/             # Governance docs
│   ├── guides/                 # Implementation guides
│   ├── reference/              # API reference
│   └── vitepress.config.ts     # VitePress config
├── scripts/                    # Helper scripts
│   ├── setup.py                # Setup utilities
│   └── validate.py             # Validation utilities
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── Taskfile.yml                # Task definitions
├── pyproject.toml              # Package metadata
└── uv.lock                     # Dependency lock
```

## Related Phenotype Projects

- **[AgilePlus](../AgilePlus)** — Specification and tracking
- **[phenotype-shared](../phenotype-shared)** — Shared libraries
- **[thegent](../thegent)** — Execution framework

## Governance & Documentation

- **CLAUDE.md** — Development standards
- **docs/governance/** — Governance policies
- **docs/guides/** — How-to documentation
- **License**: MIT

## Governance & AgilePlus

**All work tracked in AgilePlus**: `/repos/AgilePlus`
**Development Contract**: Review `CLAUDE.md` for agent operating standards and CI completeness policies.

**Quality Gates**:
```bash
task quality              # Lint, format, type check
task quality:full         # Full validation with format check
task test                 # Run test suite
task validate             # Governance & policy validation
```

## Integration with Phenotype Ecosystem

QuadSGM serves as the governance reference implementation for Python projects across Phenotype-org. Other repositories adopt its patterns for consistency.

**Use QuadSGM as a template for**:
- Task-driven development workflows
- Standardized documentation organization
- Automated policy validation
- CI/CD pipeline patterns

## Related Projects

- **[AgilePlus](../AgilePlus)** — Specification & tracking hub
- **[phenotype-shared](../phenotype-shared)** — Shared Rust utilities
- **[thegent](../thegent)** — Execution framework

## License

MIT

**Status**: Active (reference implementation)
**Maintained by**: Phenotype Org
**Last Updated**: 2026-04-24
