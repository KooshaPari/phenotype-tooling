# Changelog — pheno-scaffold-kit

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `--dry-run` flag on `pheno-scaffold init` (PR-7) — prints the sub-step plan without executing.
- New tests: `test_no_agents_md_reexport`, `test_init_scaffold_survives_failing_substep`, `test_init_scaffold_handles_missing_sub_lib`, `test_cli_dry_run`.

### Changed

- `init_scaffold` now wraps each sub-step in try/except (PR-2) — one failure surfaces as a JSON error and the rest of the run continues.
- `_call_first` no longer raises `RuntimeError` / `AttributeError` — returns `{"ok": False, "error": ...}` instead so the caller always sees a structured result.

### Removed

- `pheno-agents-md` from `dependencies` (PR-1) — it is a Rust crate, not a PyPI package, and was unimportable.
- `init_agents` and `init-agents` CLI subcommand — `pheno-agents-md` lives in the Cargo workspace, not in this Python umbrella.
- The `agents_md` entry from `SUB_LIBRARIES` and `__all__`.

### Fixed

- `pyproject.toml` build-system was malformed (`requires = ` empty, stray `["hatchling"]` block) — now uses `hatchling` properly via `requires = ["hatchling"]`.

## [0.1.0] - 2026-06-11

### Added

- Initial scaffold from V11 prep agent design (V4 §77 + §78.6).
- Umbrella CLI: `pheno-scaffold init|init-agents|init-llms|init-prompt-test|install-hooks|init-worklog`
- `detect_repo_type(repo_dir)` helper
- 5 smoke tests covering the lazy sub-lib import + `init_scaffold` orchestration
- pyproject.toml, justfile, ci.yml, deny.toml, AGENTS.md, llms.txt, .gitignore
[Unreleased]: https://github.com/KooshaPari/pheno-scaffold-kit/compare/HEAD
