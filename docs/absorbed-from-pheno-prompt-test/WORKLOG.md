## Repo creation — 2026-06-11

### Actions Taken
- Initialized `pheno-prompt-test` Python package.
- Implemented pytest plugin (`src/pheno_prompt_test/plugin.py`, 122 lines):
  - `PromptCase` dataclass (YAML schema)
  - `pytest_collectfile` hook (auto-collects `*.prompt` files)
  - `PromptFile` + `PromptTest` pytest classes
  - `prompt_case(...)` factory for programmatic use
- Wrote `AGENTS.md`, `llms.txt`, `justfile`, `CHANGELOG.md`, CI workflow.

### V4 DAG task IDs landing in this repo
- V11-CC-3 (Side CC, pheno-prompt-test) — done
- V11-16.x (L16 AX, prompt-test crutch) — scaffolded, ready for adoption

### V20 — 2026-06-12
- V20-1.3 (V20, crutch verification complete) — merged
