## Repo creation — 2026-06-11

### Actions Taken
- Initialized `pheno-llms-txt` Python package.
- Implemented `pheno_llms_txt` lib (`src/pheno_llms_txt/core.py`, 96 lines):
  - `LlmConfig` dataclass (7 fields)
  - `render(config) -> str` (TEMPLATE constant)
  - `load_config(path) -> LlmConfig`
  - `write_llms_txt(config, dest)`
- Implemented CLI (`src/pheno_llms_txt/cli.py`, 23 lines, click).
- Wrote `AGENTS.md` (eat your own dogfood, 24 lines).
- Wrote `llms.txt` (eat your own dogfood, 28 lines).
- Wrote `justfile`, `CHANGELOG.md`, CI workflow, `.gitignore`.

### V4 DAG task IDs landing in this repo
- V11-CC-2 (Side CC, pheno-llms-txt) — done
- V11-16.x (L16 AX, llms.txt crutch) — scaffolded, ready for adoption

### Blocked / Awaiting user signal
- `hatch publish` to push to PyPI (blocked on user signal)
- GitHub repo creation (blocked)
