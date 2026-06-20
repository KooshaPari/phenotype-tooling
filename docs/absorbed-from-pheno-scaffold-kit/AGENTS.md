# AGENTS.md — pheno-scaffold-kit

## Purpose

Scaffold umbrella that wires the 5 pheno-* AI-DD crutch libs into one CLI.

## Build & Test

```bash
just dev        # pip install -e ".[dev]"
just test       # pytest -v
just lint       # ruff check
```

## Repo conventions

- Uses hatchling (PEP 517/621)
- src/ layout (PEP 328)
- pytest with `pythonpath = ["src"]` so tests import from src/pheno_scaffold_kit
- Click for the CLI

## Sub-library contract

pheno-scaffold-kit imports each sub-lib **lazily** and **defensively** —
`try: import pheno_agents_md except ImportError: pheno_agents_md = None`.
The umbrella must work even if 0 of the 5 sub-libs are installed (degraded
behavior is fine; tests use monkeypatch.setattr to inject mocks).

The umbrella's `init_agents / init_llms / init_prompt_test / install_hooks / init_worklog`
each call into the sub-lib's first-available entrypoint in a fixed order:
`("init_<name>", "init", "scaffold")`.

## Do Not Touch

- `src/pheno_scaffold_kit/__init__.py` — the SUB_LIBRARIES dict and the
  `_call_first` helper are the API contract.
- `pyproject.toml` dependencies list — only add a sub-lib if you bump its
  major version. New sub-libs get a new release + an entry here.

## Reference

- See `/Users/kooshapari/CodeProjects/Phenotype/repos/FLEET_100TASK_DAG_V4.md`
  §77 (V12 EXTENSION) and §78.3 (V13 EXTENSION).
- See `pheno-agents-md`, `pheno-llms-txt`, `pheno-prompt-test`,
  `pheno-vibecoding-guard`, `pheno-worklog-schema` for the 5 sub-libs.
