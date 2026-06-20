# pheno-scaffold-kit

Scaffold umbrella for Phenotype repository hygiene tools:

- `pheno-agents-md`
- `pheno-llms-txt`
- `pheno-prompt-test`
- `pheno-vibecoding-guard`
- `pheno-worklog-schema`

Plus 3 governance tools absorbed 2026-06-19 from retired standalone repos:

- `pheno-predict` (L72, ADR-047) — token-shingle Jaccard scanner for predictive DRY
- `pheno-framework-lint` (L73, ADR-048) — substrate graduation & tier-convention linter
- `pheno-drift-detector` (L74, ADR-049) — app-substrate drift detection

`pheno-scaffold-kit` provides one installable CLI and a small Python API that wires the eight scaffold libraries together.

## Install

```bash
uv add pheno-scaffold-kit
```

For local development:

```bash
uv sync --all-extras --dev
```

## CLI

Initialize everything for a repository:

```bash
pheno-scaffold init /path/to/repo
```

Run individual setup steps:

```bash
pheno-scaffold init-agents /path/to/repo
pheno-scaffold init-llms /path/to/repo
pheno-scaffold init-prompt-test /path/to/repo
pheno-scaffold install-hooks /path/to/repo
pheno-scaffold init-worklog /path/to/repo
```

The unified `init` command detects basic repository traits, then runs all five scaffold steps in a stable order:

1. Agents guidance
2. LLM context files
3. Prompt tests
4. Vibecoding guard hooks
5. Worklog schema

## Python API

```python
from pheno_scaffold_kit import init_scaffold

result = init_scaffold("/path/to/repo")
print(result)
```

Each sub-library is also re-exported from `pheno_scaffold_kit` for direct access.

## Development

```bash
uv run pytest
uv run pheno-scaffold --help
```

## Package Layout

```text
src/pheno_scaffold_kit/
  __init__.py
  cli.py
tests/
  test_smoke.py
```
