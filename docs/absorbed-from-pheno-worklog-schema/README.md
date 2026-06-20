# pheno-worklog-schema

> WORKLOG.md schema + validator for Phenotype repos.

This is the canonical implementation of the **`pheno-worklog-schema`** AI-DD
crutch described in `FLEET_100TASK_DAG_V4.md` §70.3 + §77.4.

## What it does

Defines a strict v2 schema for `WORKLOG.md` files (a markdown table with
columns `Date | Task ID | Layer | Action | Files | Notes`) and provides:

- A Python parser (`parse_worklog`) that extracts the table rows.
- A validator (`validate_entry`) that checks each row against the canonical
  layer set, action set, and task ID regex.
- A CLI (`pheno-worklog-validate`) for use in CI or pre-commit.

## Install

```bash
pip install pheno-worklog-schema
```

## Usage

### Validate a WORKLOG.md

```bash
$ pheno-worklog-validate ./WORKLOG.md
12 entries, 0 with errors
$ echo $?
0
```

### As a Python lib

```python
from pheno_worklog_schema import parse_worklog, validate_entry
from pathlib import Path

entries = parse_worklog(Path("WORKLOG.md"))
for e in entries:
    errs = validate_entry(e)
    if errs:
        print(f"{e.date} {e.task_id}: {errs}")
```

## Schema

| Column | Type | Rule |
|--------|------|------|
| `Date` | ISO-8601 (`YYYY-MM-DD`) | `date.fromisoformat()` |
| `Task ID` | string | must match `^V\d+-\d+(\.\d+)*$` |
| `Layer` | enum | L1-L16, Side-A-Z, Side-AA-ZZ, or "Meta" |
| `Action` | enum | commit, merge, close, archive, doc, plan, deploy, release |
| `Files` | list[str] | comma-separated paths; at least one |
| `Notes` | string | free-form |

## Example valid row

```
| 2026-06-11 | V4-1.1.1 | L1 | commit | L1_TRIAGE_2026_06_11.md | 78 dirty files untouched |
```

## Eat your own dogfood

This repo uses itself. See [`WORKLOG.md`](WORKLOG.md) for a real example.

## License

MIT
