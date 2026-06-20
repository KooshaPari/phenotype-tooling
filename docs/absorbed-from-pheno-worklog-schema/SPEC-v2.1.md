# pheno-worklog-schema v2.1 — Specification

**Status:** CURRENT (supersedes v2.0)
**Effective:** 2026-06-17
**ADR:** [ADR-015](../../docs/adr/2026-06-15/ADR-015-worklog-v2-1-device-column.md), [ADR-023](../../docs/adr/2026-06-15/ADR-023-agent-effort-governance.md)
**Deprecates:** v2.0 (10-column) — readers still supported until 2026-06-22

## Summary

v2.1 adds one new column to the existing v2.0 10-column schema:

| | v2.0 (10-col) | v2.1 (11-col) |
|---|---|---|
| Columns | 10 | **11** (+ `device`) |
| Position | — | between `author` and `notes` (position 10, 0-indexed) |

**No other column changes.** All v2.0 rows are still parseable; the new `device` field defaults to `""` (empty) for v2.0 rows and is reported in `stats()["missing_device"]`.

## The 11 v2.1 Columns

| # | Column | Type | Required | Allowed values | Notes |
|---|---|---|---|---|---|
| 0 | `task_id` | string | yes | `V\d+-[A-Z0-9]+(?:[.\-][A-Z0-9]+)*` (regex) | E.g. `V7-3-1`, `V11-CC-5`, `L5-104-4` |
| 1 | `date` | string | yes | ISO-8601 `YYYY-MM-DD` | |
| 2 | `repo` | string | no | free-form | E.g. `KooshaPari/AgilePlus` |
| 3 | `category` | string | no | free-form | E.g. `L1-Stabilize`, `Side-A-lib`, `V12-crutch` |
| 4 | `title` | string | no | free-form | Short PR title |
| 5 | `commit_sha` | string | no | 7-40 char hex | Empty if not yet committed |
| 6 | `pr_number` | int | no | positive int | Empty if no PR yet |
| 7 | `status` | enum | no | `open` \| `in_progress` \| `merged` \| `closed` \| `abandoned` \| `deferred` | |
| 8 | `author` | string | no | free-form | GitHub handle |
| 9 | `device` | enum | **yes (v2.1)** | `macbook` \| `heavy-runner` \| `subagent` \| `ci` \| `""` | **NEW in v2.1.** See ADR-023 device-fit gate below |
| 10 | `notes` | string | no | free-form | |

## The `device` Column (ADR-023)

**Purpose:** Records where the work was performed, enabling the device-fit gate (ADR-023) and Fleet-wide distribution analysis.

**Allowed values:**

| Value | When to use | Example use cases |
|---|---|---|
| `macbook` | Light work on the user's MacBook | Planning, ADRs, small focused PRs, code review, dogfooding |
| `heavy-runner` | Heavy work on a self-hosted runner or dispatched subagent | `cargo test --workspace` on 100+ crates, iOS Simulator boot, Docker-in-Docker tests, Unity/Unreal editor head, any single build/test > 10 min wall |
| `subagent` | Work performed by a subagent (dispatch-mcp / forge / muse) | Any task dispatched via `/forge` CLI, `task` tool, or `dispatch-mcp` |
| `ci` | Work performed by a CI runner | GitHub Actions, Jenkins, etc. |
| `""` (empty) | Legacy v2.0 rows only | Will be flagged in `stats()["missing_device"]` until 2026-06-22 |

**Default for new entries:** `macbook` (most entries are light work).

## Migration from v2.0

**Migration date:** 2026-06-22 (5 days from spec authoring)
**Status:** BACKWARDS COMPATIBLE — v2.0 readers continue to work; v2.0 writers are deprecated.

### For consumers (readers)
- v2.0 (10-col) WORKLOG.md files: **still parseable** by v2.1
- v2.1 (11-col) WORKLOG.md files: **not parseable** by v2.0 (will read missing column 9 as a partial cell)

### For producers (writers)
- New entries should always include the `device` column with a non-empty value
- Existing v2.0 rows can stay as-is until 2026-06-22
- After 2026-06-22, `stats()["missing_device"]` should be 0 across the fleet

### Migration script

`migrate_v2_to_v2_1.py` (in this repo) provides:
- `migrate_file(path)`: in-place upgrade of a v2.0 file to v2.1 (adds empty `device` column to all rows)
- `migrate_repo(root)`: walks a repo and migrates all WORKLOG.md files
- `is_v21(path)`: returns True if file has the 11-column v2.1 header

## Stats (v2.1 additions)

```python
from pheno_worklog_schema import parse_worklog, stats

entries = parse_worklog("WORKLOG.md")
s = stats(entries)
# s["by_device"] = {"macbook": 5, "heavy-runner": 2, "subagent": 1, "": 3}
# s["missing_device"] = 3  # count of v2.0 legacy rows
```

## Validation (v2.1 additions)

`validate_row(cols)` now accepts both 10-col and 11-col rows. For 11-col rows, the `device` value must be in `CANONICAL_DEVICES` (or `""` for legacy). For 10-col rows, no device validation is performed.

## JSONL audit trail emission (ADR-032)

The markdown `WORKLOG.md` is the canonical source of truth. The JSONL
audit trail is the derived artifact that downstream tooling (CI
ingestion, fleet analytics, 71-pillar audit) consumes. Per
[ADR-032](../../docs/adr/2026-06-17/ADR-032-pheno-worklog-schema-decision.md)
§ "JSONL audit trail":

```
pheno-worklog-schema WORKLOG.md  →  validator  →  worklogs/{date}-L*.jsonl
                                               (one JSON object per line)
```

### JSONL schema (13 fields, ADR-032 canonical)

| # | Field | Type | Source |
|---|---|---|---|
| 0 | `date` | string (ISO-8601) | markdown `date` column |
| 1 | `task_id` | string | markdown `task_id` column |
| 2 | `layer` | string | `WorklogEntry.layer` (V2 parser maps markdown `category` → `layer` at parse time) |
| 3 | `action` | string | `WorklogEntry.action` (V2 parser: `"merge"` if status is `"merged"`, else `"commit"`) |
| 4 | `files` | string (comma-joined) | `WorklogEntry.files` (empty in v2.0/v2.1 markdown — column not present) |
| 5 | `notes` | string | markdown `notes` column |
| 6 | `status` | enum | markdown `status` column |
| 7 | `branch` | string | **derived downstream from CI / git** — emitted as `""` here |
| 8 | `commit` | string | markdown `commit_sha` column (empty if None) |
| 9 | `pr` | int \| null | markdown `pr_number` column (JSON null if None) |
| 10 | `device` | enum | markdown `device` column (empty for legacy v2.0 rows) |
| 11 | `derived_at` | string (ISO-8601 `Z`) | generation timestamp (UTC) — defaults to now |
| 12 | `tool_version` | string | `pheno_worklog_schema.__version__` (overridable) |

### Python API

```python
from pathlib import Path
from pheno_worklog_schema import emit_jsonl, worklog_entry_to_json, JSONL_FIELDS

# File-level emission (the typical case)
n = emit_jsonl("WORKLOG.md", "worklogs/2026-06-18-T14-3.jsonl")
# Returns the number of entries written. An empty WORKLOG.md yields
# an empty output file and returns 0.

# With explicit provenance
n = emit_jsonl(
    "WORKLOG.md",
    "worklogs/2026-06-18-T14-3.jsonl",
    derived_at="2026-06-18T12:34:56Z",  # ISO-8601 UTC; default: now()
    tool_version="0.2.0",               # default: pheno_worklog_schema.__version__
)

# Single-entry conversion (one parsed WorklogEntry → one JSONL line)
from pheno_worklog_schema import parse_worklog
entries = parse_worklog("WORKLOG.md")
line = worklog_entry_to_json(
    entries[0],
    derived_at="2026-06-18T12:34:56Z",
    tool_version="0.2.0",
)
```

### CLI

```bash
# Module form (no install required; uses PYTHONPATH=src)
python3 -m pheno_worklog_schema.emit_jsonl WORKLOG.md OUTPUT.jsonl

# Console-script form (after `pip install pheno-worklog-schema`)
pheno-worklog-emit WORKLOG.md OUTPUT.jsonl \
    [--derived-at 2026-06-18T12:34:56Z] \
    [--tool-version 0.2.0]
```

Exit codes:
- `0` — success
- `2` — WORKLOG.md missing or unreadable

### Field-mapping notes

- `layer` ← markdown `category` (the V2 parser sets `entry.layer` from
  the markdown `category` column at parse time). If a `WorklogEntry` is
  constructed manually, `layer` defaults to `"L?"`.
- `action` ← markdown status-derived heuristic (the V2 parser sets
  `entry.action` to `"merge"` if status is `"merged"`, else `"commit"`).
  If a `WorklogEntry` is constructed manually, `action` defaults to
  `"commit"`.
- `files` is always emitted as a comma-joined string. For v2.0/v2.1
  markdown (which has no `files` column), this is the empty string `""`.
- `branch` is **not** present in the v2.1 markdown schema. The JSONL
  emitter emits `""`; consumers should derive the branch from CI / git
  context (e.g. `git rev-parse --abbrev-ref HEAD` at audit time).
- `pr` is JSON `null` when the markdown `pr_number` is empty.
- `device` is `""` for legacy v2.0 rows (no `device` column).

### Where this sits in the ADR-032 layered model

| Layer | Format | Source of truth | Author | Validation |
|---|---|---|---|---|
| **Schema** | Markdown table (`WORKLOG.md`) | YES — what was done | Human (orchestrator / forge subagent) | Strict |
| **Audit trail** | JSONL (one object per line) | NO — derived | Tool (`emit_jsonl` + cron) | Schema-conformant JSON |

Markdown is canonical, JSONL is derived. No merge, no deprecation, no
consolidation — both layers exist. See ADR-032 for the full rationale.

## Versioning

- This package version: `0.2.0` (per `pyproject.toml`)
- Schema version: `v2.1`
- Deprecation horizon: v2.0 readers supported until 2026-06-22

## Tolerated legacy formats (deprecation sweep, 2026-06-18)

The fleet contains three pre-substrate formats that the v2.1 validator
**recognizes and migrates** rather than rejects. These are accepted
variants, not violations.

### Format taxonomy

| Format | Header columns | Source | Migration path |
|---|---|---|---|
| **v2.1** (canonical) | 11 — `task_id \| date \| repo \| category \| title \| commit_sha \| pr_number \| status \| author \| device \| notes` | new entries from 2026-06-17+ | none — this IS the target |
| **v2.0** | 10 — v2.1 with `device` missing | entries before 2026-06-17, or 4 fleet WORKLOG.md files migrated 2026-06-17 | `migrate_v2_to_v2_1.py` adds empty `device` column |
| **v1+device** (hybrid) | 7 — `Date \| Task ID \| Layer \| Action \| Files \| Notes \| device` | 4 fleet WORKLOG.md files (pheno-config, pheno-context, pheno-otel, pheno-port-adapter) that bolted `device` onto the v1 substrate schema | `migrate_v2_to_v2_1.py` rewrites header + each row |
| **v1** (oldest) | 6 — v1+device without `device` | 2 fleet WORKLOG.md files (pheno-go-ctxkit, Parpoura-5th/docs) — pure pre-substrate format | `migrate_v2_to_v2_1.py` rewrites header + each row; auto-detects `device` per row (macbook is the safe default for Go contexts) |

### Why the tolerated variants exist

- The fleet began tracking work in `WORKLOG.md` files long before
  the `pheno-worklog-schema` v2.0 substrate was introduced.
- The substrate introduced a 10-column machine-readable format
  (`task_id | date | repo | category | title | commit_sha | pr_number | status | author | notes`).
- v2.1 added the 11th `device` column for ADR-023 device-fit gate
  enforcement.
- Existing v1 worklogs were never retroactively rewritten, and
  ad-hoc `device:` columns were bolted onto some files when
  users started tagging work.
- The 2026-06-18 deprecation sweep (L5-103) consolidated all
  three tolerated formats into the migration script and validator
  so the cutover on 2026-06-22 can be enforced without orphaning
  pre-substrate files.

### Validation policy

- **New `WORKLOG.md` files** (untracked at validator runtime) → `device:` column is **REQUIRED** (validator FAILS if missing).
- **Tracked `WORKLOG.md` files in v2.0** → WARN only until 2026-06-22; FAIL on/after 2026-06-22.
- **Tracked `WORKLOG.md` files in v1 or v1+device** → WARN only indefinitely; per-repo migration PR is the path to v2.1.
- **Tracked `WORKLOG.md` files in v2.1** → always PASS.
- **`--warn-only` flag** → suppresses all FAILs and is the
  recommended pre-commit invocation in 2026-06-18 → 2026-06-21.

## See also

- [ADR-015: WORKLOG v2.1 device column](../../docs/adr/2026-06-15/ADR-015-worklog-v2-1-device-column.md) — original ADR
- [ADR-023: Agent effort governance](../../docs/adr/2026-06-15/ADR-023-agent-effort-governance.md) — device-fit gate
- [ADR-032: WORKLOG format = markdown schema + JSONL audit trail](../../docs/adr/2026-06-17/ADR-032-pheno-worklog-schema-decision.md) — JSONL audit trail rationale
- [`migrate_v2_to_v2_1.py`](./migrate_v2_to_v2_1.py) — migration script (handles v1, v1+device, v2.0, v2.1)
- [`validate_worklog.py`](./validate_worklog.py) — standalone validator for pre-commit/lefthook
- [`src/pheno_worklog_schema/emit_jsonl.py`](./src/pheno_worklog_schema/emit_jsonl.py) — JSONL audit trail emitter (ADR-032)
- [`tests/test_emit_jsonl.py`](./tests/test_emit_jsonl.py) — JSONL emitter tests (28 tests)
- [`findings/2026-06-18-L5-103-v2-1-deprecation-sweep.md`](../../findings/2026-06-18-L5-103-v2-1-deprecation-sweep.md) — sweep execution log
- [`findings/2026-06-18-T11-4-T14-3-jsonl-emission.md`](../../findings/2026-06-18-T11-4-T14-3-jsonl-emission.md) — JSONL emission execution log (this change)
- [`README.md`](./README.md) — quickstart
