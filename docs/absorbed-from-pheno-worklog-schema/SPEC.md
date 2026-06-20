# pheno-worklog-schema — SPEC

## Scope

WORKLOG.md schema + validator for Phenotype repos. Defines a strict v2.1
schema (markdown table with 10 columns) and provides:

- a Python parser (`parse_worklog`) that extracts the table rows;
- a validator (`validate_row`) that checks each row against the canonical
  layer/action/status sets and the v2.1 task-id regex;
- a CLI (`pheno-worklog-validate`) for use in CI or pre-commit.

Implements V4 §70.3 + §77.4 of `FLEET_100TASK_DAG_V4.md`, and the v2.1
`device:` column bump from ADR-015 / ADR-025.

## Public API

- `class WorklogEntry` — dataclass with the 10 v2.1 columns.
- `parse_worklog(path: Path) -> list[WorklogEntry]` — markdown table → entries.
- `validate_row(cols: list[str]) -> list[str]` — v2 10-column validator.
- `validate_entry(entry: WorklogEntry) -> list[str]` — v1 6-column validator.
- `to_jsonl(entries: list[WorklogEntry]) -> list[str]` — JSONL export.
- `stats(entries: list[WorklogEntry]) -> dict` — counts per layer/action/status.
- `add_entry(path: Path, entry: WorklogEntry) -> str` — append a new row.
- `WORKLOG_COLUMNS`, `EXPECTED_COLUMNS`, `COLUMN_NAMES` — column metadata.
- `TASK_ID_RE` — `^V\d+-\d+(\.\d+)*$`.
- `CANONICAL_LAYERS`, `CANONICAL_LAYERS_OR_SIDE`, `CANONICAL_ACTIONS`,
  `CANONICAL_STATUS` — enum sets.
- `init_worklog(repo_dir: str | Path) -> dict` — V6 PR-6 scaffold-kit entrypoint.

## CLI

```bash
pheno-worklog-validate ./WORKLOG.md
# exit 0 if all valid, 1 if any errors
```

## Conventions

- **When to use:** every pheno-* repo maintains a WORKLOG.md.
- **When NOT to use:** ad-hoc repos not on the V2.1 schema.
- **5-line quickstart:**
  ```python
  from pathlib import Path
  from pheno_worklog_schema import parse_worklog, validate_row
  for row in parse_worklog(Path("WORKLOG.md")):
      errs = validate_row([getattr(row, c) for c in WORKLOG_COLUMNS])
      if errs:
          print(errs)
  ```

## Schema (v2.1, 10 columns)

| Column | Type | Rule |
|---|---|---|
| `Date` | ISO-8601 | `YYYY-MM-DD` |
| `Task ID` | string | `V\d+-\d+(\.\d+)*` |
| `Layer` | enum | L1-L16, Side-A-ZZ, "Meta" |
| `Action` | enum | commit, merge, close, archive, doc, plan, deploy, release |
| `Files` | list[str] | comma-separated paths; ≥1 |
| `Notes` | string | free-form |
| `Status` | enum | planned, doing, for_review, done, blocked |
| `Author` | string | free-form |
| `Device` | enum | macbook, heavy-runner, subagent, ci |
| `Pr` | int | PR number or 0 |

The detailed v2.1 schema bump rationale lives in `SPEC-v2.1.md`.

## Quality bar

- 71-pillar score: 24/71 (Tier 0)
- Test matrix: 6+ unit tests in `tests/test_schema.py`
- Coverage: pending measurement
- License: dual (MIT + Apache-2.0)

## See also

- ADR-023 (Rule 3.1 substrate quality bar)
- ADR-025 (v2.1 schema bump, `device:` column)
- V4 §77.4 (worklog-schema crutch adoption)