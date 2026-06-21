# Merge Prep Summary — `integration/consolidate`

## What this consolidates
- **Documentation** — CONTRIBUTING.md stub, Quick Start section in README, work-state header updated to "Active Development"
- **Security & CI hygiene** — Removed custom CodeQL workflows (relying on GitHub default setup), patchable CVE dependency bumps in `Cargo.lock`/`uv.lock`
- **Repository hardening** — `.gitignore` hardened against build/cache artifacts (two incremental passes)
- **Test coverage** — Unit tests for Python models `to_dict` functions; new Rust unit tests for `ToolError` I/O and JSON conversions

## Tests added
| Test file | Coverage |
|---|---|
| `python/tests/test_models.py` | `to_dict` round-trips for all core models (refactored from 265-line boilerplate to 75 focused assertions) |
| `crates/pheno-mcp-defs/tests/tool_error_from_io.rs` | `ToolError` conversion from `std::io::Error` |
| `crates/pheno-mcp-defs/tests/tool_error_from_json.rs` | `ToolError` conversion from JSON errors |

## Traceability
- `docs/traceability.md` maps requirements **FR-PHENOMCP-001 → FR-PHENOMCP-006** to source files and test files.
- All consolidated branches are docs-, chore-, fix-, or test-level; no new functional requirements introduced.

## Build status
- `cargo check --workspace` — **0 errors** (verified in `BUILD_STATUS.md`, commit `731ef7c`)
- GitHub Actions workflows are enrolled but **billing-blocked org-wide**; no live CI regressions expected.

## Merge risk
**Low** — Changes are limited to documentation, patch-level dependency bumps, `.gitignore` hardening, and additive unit tests. No public API surface changes, no breaking schema modifications, and no new runtime dependencies.
