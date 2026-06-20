# ARCHITECTURE — pheno-scaffold-kit

## Overview

pheno-scaffold-kit is a **scaffold umbrella** — a thin Python CLI that wires
5 AI-DD crutch libraries plus 3 absorbed governance tools into a single
entrypoint. It provides no standalone logic; its job is orchestration and
defensive import.

```
User → `pheno-scaffold init <repo>`
         │
         ├── detect_repo_type()     — trait detection (git/python/node/rust/go)
         │
         ├── init_llms()            → pheno-llms-txt (PyPI)
         ├── init_prompt_test()     → pheno-prompt-test (PyPI)
         ├── install_hooks()        → pheno-vibecoding-guard (PyPI)
         ├── init_worklog()         → pheno-worklog-schema (PyPI)
         │
         ├── framework-lint check   → _framework_lint.py (absorbed L73)
         ├── drift-detector scan    → _drift_detector.py (absorbed L74)
         └── predict scan           → _predict.py (absorbed L72)
```

## Component Architecture

### 1. Public API (`__init__.py`)

- **Lazy sub-library loading** — each sub-lib is import-guarded via
  `try: import pheno_llms_txt except ImportError: pheno_llms_txt = None`,
  so the umbrella works even if 0 of the 5 PyPI packages are installed.
- `_call_first(module, names, repo_dir, **kwargs)` — calls the first
  available entrypoint in `("init_<name>", "init", "scaffold")` order.
- `detect_repo_type()` — filesystem probe for `.git`, `pyproject.toml`,
  `Cargo.toml`, `package.json`, `go.mod`.

### 2. CLI Layer (`cli.py`)

Built on **Click**. Groups:

| Command | Purpose |
|---------|---------|
| `init` | Run all 4 scaffold steps (with `--dry-run` support) |
| `init-llms` | Bootstrap llms.txt |
| `init-prompt-test` | Bootstrap prompt test harness |
| `install-hooks` | Drop pre-commit-config.yaml |
| `init-worklog` | Drop WORKLOG.md |
| `framework-lint check` | L73 per-repo tier lint |
| `framework-lint check-all` | L73 bulk fleet scan |
| `drift-detector scan` | L74 drift hit scan |
| `drift-detector validate` | L74 HITL gate |
| `predict scan` | L72 predictive-DRY scan |
| `predict check-criteria` | L72 4-criteria filter |

### 3. Absorbed Tools (inline modules)

Three tools were absorbed 2026-06-19 from standalone repos:

| Module | Source | ADR | Function |
|--------|--------|-----|----------|
| `_predict.py` | `pheno-predict` | ADR-047 (L72) | Token-shingle Jaccard scanner for predictive DRY |
| `_framework_lint.py` | `pheno-framework-lint` | ADR-048 (L73) | Substrate graduation & tier-convention linter |
| `_drift_detector.py` | `pheno-drift-detector` | ADR-049 (L74) | App-substrate drift detection |

Each exposes `cmd_scan`, `cmd_check` etc. via argparse, and the Click CLI
wraps these with `_fl.argparse.Namespace(...)` call forwarding.

### 4. Sub-library Contract

Each sub-lib exposes one of `init_<name>`, `init`, or `scaffold` which
accepts `(repo_dir: Path, **kwargs) -> dict`. Returns `{"ok": bool, ...}`.

## Key Design Decisions

- **No hard dependencies** on sub-libs — all imports are guarded.
- **Per-step try/except** — one sub-step failing returns JSON error without
  aborting the rest (V6 PR-2).
- **Absorbed tools keep their argparse CLI** — the Click glue uses
  `argparse.Namespace` forwarding, minimizing change risk.
- **No AST parsing** — all heuristics are file-presence + regex, keeping
  the absorbed tools fast and dependency-free.

## Quality Bar

- 71-pillar score: 23/71 (Tier 0)
- Test matrix: 5 smoke tests + absorbed-tool coverage + property-based tests
- License: MIT + Apache-2.0 (dual)

## See Also

- `AGENTS.md` — contributor onboarding, build/test commands
- `SPEC.md` — public API reference, CLI usage, quickstart
- ADR-023 (Rule 3.1 substrate quality bar)
- V4 §77 (V12 EXTENSION), §78.3 (V13 EXTENSION)
