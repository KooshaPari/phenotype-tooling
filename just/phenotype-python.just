# phenotype-python.just — Phenotype-org shared Python recipe library.
# Import from a per-repo justfile via:
#   import? "path/to/phenotype-python.just"

# Show the available recipes
default:
  @just --list

# Sync dependencies via uv (creates/updates the venv)
install:
  uv sync

# Run the pytest test suite
test:
  pytest

# Lint with ruff (lint rules)
lint:
  ruff check

# Format with ruff (formatter)
fmt:
  ruff format

# Type check with mypy
typecheck:
  mypy .

# Full local CI sweep — runs every gate, stops on first failure
ci:
  @just lint
  @just fmt
  @just typecheck
  @just test

# Remove caches and build artifacts
clean:
  rm -rf .pytest_cache .ruff_cache .mypy_cache dist build
  find . -type d -name __pycache__ -exec rm -rf {} +
