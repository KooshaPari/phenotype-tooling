# quality-gate human summary mode

## Context

`quality-gate` is the org-wide Rust CLI that replaces duplicated
`quality-gate.sh` scripts. Today it is positioned as a JSON-emitting gate for
CI, with `--path`, `--skip-fmt`, `--skip-clippy`, and `--skip-test` flags.
That makes it good for machines, but a little awkward for local developer
loops where the main need is a quick yes/no summary and the failing step name.

## Proposal

Add a human-readable output mode for local use while keeping JSON as the
machine-friendly default.

Suggested shape:

- `--format json` keeps the current structured report behavior.
- `--format human` prints a concise step summary such as `fmt: passed`,
  `clippy: skipped`, and an overall `all_passed` line.
- `--format auto` can later choose human output for TTYs and JSON for CI, but
  this spec does not require auto-detection in the first increment.

## Why this is high value

This is a small ergonomics win for the most common developer workflow:
running the gate locally before pushing. It reduces the need to inspect JSON by
eye, keeps CI unchanged, and does not alter the actual quality checks.

## Scope

- Keep the existing pass/fail semantics unchanged.
- Keep the existing skip flags unchanged.
- Keep JSON output available for automation.
- Do not change the underlying fmt/clippy/test execution order.

## Acceptance Criteria

- The CLI accepts an explicit output-format flag.
- JSON output remains available and stable for automation.
- Human output is concise, readable, and includes per-step status plus the
  overall result.
- The change is reversible without affecting the quality-gate execution model.

## Out of Scope

- No change to command execution behavior.
- No new dependency on external services.
- No repository-wide rollout automation.

## Traceability

- Related FR/NFR/issue ID: none found in the current repo docs or open issues.
