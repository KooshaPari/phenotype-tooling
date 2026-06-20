# Changelog

## [Unreleased]

### Fixed
- **Parser format-strictness bug** (L5-103.x): `parse_worklog()` and
  `add_entry()` used literal-string checks (`if "| task_id" in text.lower()`)
  that only accepted the spaced v2 header style (`| task_id | date | ...`).
  The migration script `migrate_v2_to_v2_1.py` produces the unspaced style
  (`|task_id|date|...`) by default, so the substrate's own WORKLOG.md —
  written by PR #2 — was rejected by the parser and parsed to 0 entries.
  The bug was masked by a vacuous `test_self_worklog_validates` (the loop
  body never executed when `entries == []`). Replaced with a column-count
  + first-cell based detector (`_is_v2_header_line` / `_has_v2_header`)
  that accepts both styles. `add_entry` now also auto-detects the existing
  file's row style (spaced vs unspaced) so it does not introduce a second
  style into the same file. Added 2 regression tests
  (`test_parse_worklog_unspaced_v2_1_header`,
  `test_parse_worklog_unspaced_v2_0_legacy_header`) and strengthened
  `test_self_worklog_validates` to assert `len(entries) > 0` so this bug
  class can never recur silently. After the fix, the substrate's own
  WORKLOG.md parses to 12 entries; `stats.missing_device` drops from 12
  to 0 once the 12 historical V11-CC-5 / V20-1.5 rows are backfilled with
  `device: macbook` (the correct value for MacBook scaffold-kit work).

## [0.2.0] - 2026-06-18

### Added
- `device:` column in `EXPECTED_COLUMNS`, `COLUMN_NAMES` (11-col v2.1 schema per ADR-025).
- `CANONICAL_DEVICES` constant: `["macbook", "heavy-runner", "subagent", "ci"]`.
- `validate_row` now checks device column position 9 for valid device values.
- `migrate_v2_to_v2_1.py` migration script: auto-detects v1 (6-col), v1+device (7-col), v2.0 (10-col) and converts to canonical v2.1 (11-col).
- `validate_worklog.py` pre-commit validator: checks v2.1 conformance, warns on legacy formats before 2026-06-22 cutover, fails after.
- `cli.py`: `pheno-worklog-validate` now requires device values in v2.1 rows.

### Changed
- Bumped version from 0.1.0 to 0.2.0 to reflect v2.1 schema break (new column).
- `WORKLOG_COLUMNS` updated from 10 to 11 columns.

## [0.1.0] - 2026-06-11

### Added
- First release.
