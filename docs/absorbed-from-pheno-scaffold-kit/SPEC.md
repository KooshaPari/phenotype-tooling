# pheno-scaffold-kit — SPEC

## Scope

Scaffold umbrella CLI that wires the 5 pheno-* AI-DD crutch libraries into a
single entrypoint. Calling `pheno-scaffold init <repo>` runs all 5 scaffold
steps in a stable order; each step is wrapped in try/except so a single
failure surfaces as a JSON error without aborting the rest of the run.

Implements V4 §77 (V12 EXTENSION) + §78.3 (V13 EXTENSION) of
`FLEET_100TASK_DAG_V4.md`.

## Public API

- `SUB_LIBRARIES: dict[str, ModuleType | None]` — the 4 lazily-imported
  sub-libraries (`llms_txt`, `prompt_test`, `vibecoding_guard`, `worklog_schema`).
- `detect_repo_type(repo_dir: str | Path) -> dict[str, bool]` — returns
  `{exists, git, python, node, rust, go}` flags.
- `init_llms(repo_dir, **kwargs)` — bootstrap llms.txt + config.
- `init_prompt_test(repo_dir, **kwargs)` — bootstrap prompt test harness.
- `install_hooks(repo_dir, **kwargs)` — drop `.pre-commit-config.yaml`.
- `init_worklog(repo_dir, **kwargs)` — drop a starter WORKLOG.md.
- `init_scaffold(repo_dir, **kwargs) -> dict` — run all 4 steps in order,
  returning a `{repo_dir, repo_type, llms, prompt_test, hooks, worklog}` dict
  where each step is a `{ok: bool, ...}` sub-result.

## CLI

```
pheno-scaffold init /path/to/repo
pheno-scaffold init-llms /path/to/repo
pheno-scaffold init-prompt-test /path/to/repo
pheno-scaffold install-hooks /path/to/repo
pheno-scaffold init-worklog /path/to/repo
pheno-scaffold init /path/to/repo --dry-run
```

## Conventions

- **When to use:** bootstrapping a new pheno-* repo or adopting the 5
  AI-DD crutches into an existing repo.
- **When NOT to use:** non-Python repos that cannot install the sub-libraries.
- **5-line quickstart:**
  ```python
  from pheno_scaffold_kit import detect_repo_type, init_scaffold
  if detect_repo_type(".")["python"]:
      print(init_scaffold("."))
  ```

## Sub-library contract

Each sub-lib is imported lazily + defensively:

```python
try:
    import pheno_llms_txt as llms_txt
except ImportError:
    llms_txt = None
```

The umbrella works even if 0/4 sub-libs are installed (degraded behavior
returns `{ok: False, error: "sub-library not installed"}`).

## Quality bar

- 71-pillar score: 23/71 (Tier 0)
- Test matrix: 5 smoke tests covering lazy imports + orchestration
- Coverage: pending measurement
- License: dual (MIT + Apache-2.0)

## See also

- ADR-023 (Rule 3.1 substrate quality bar)
- V4 §78.3 (V13 EXTENSION, scaffold-kit substrate)