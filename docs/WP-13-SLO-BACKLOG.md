# WP-13 — SLO-driven backlog

## Goal

Close the loop between Prometheus burn-rate alerts and the GitHub
issue tracker. Every firing `PhenotypeCli*` alert owned by this repo
becomes exactly one GitHub issue within ten minutes, deduped by an
immutable fingerprint so the same alert can't open duplicate issues
during a single incident.

## Why this matters

WP-09 wired the metrics + dashboards + alerts. WP-13 wires the
**outcome**: an alert that nobody notices is the same as no alert.

## Surface

| File | Purpose |
|------|---------|
| `scripts/slo_backlog.py` | Polls Prometheus `/api/v1/alerts`, dedupes against open issues via `gh`, opens new ones with PTX-aligned severity prefix |
| `.github/workflows/slo-backlog.yml` | Runs `slo_backlog.py` every 10 min + on `workflow_dispatch` |

## How it works

1. The Prometheus rules at `observability/prometheus/phenotype-tooling.rules.yml`
   define three owned alerts: `PhenotypeCliSuccessRateFastBurn`,
   `PhenotypeCliSuccessRateSlowBurn`, `PhenotypeCliStartupLatencyP95`.
2. `slo_backlog.py` calls `GET /api/v1/alerts` and filters to those
   three alertnames (`ALERT_OWNERS` constant).
3. For each firing alert, compute a 12-hex SHA-1 fingerprint over
   `alertname + slo`. Skip if any open issue title contains the same
   fingerprint in `[fp=...]`.
4. Otherwise render an issue body from the alert's labels +
   annotations + the runbook link, then `gh issue create` with the
   severity-appropriate label set.
5. The issue auto-closes once the alert clears from Prometheus — the
   closing workflow will be added in WP-14 alongside the alert
   manager.

## Exit-code contract

| Code | Meaning |
|------|---------|
| 0    | success (zero or more issues opened) |
| 1    | usage / config error |
| 2    | network error fetching `/api/v1/alerts` |
| 3    | `gh issue list/create` failure |

## Severity labels

Aligned with the PTX severity tier rules established in WP-11:

| Prometheus `severity` | Title prefix | GitHub labels |
|-----------------------|--------------|---------------|
| `critical`            | `phase1:crit` | `slo-incident`, `severity:phase1-crit`, `needs-triage` |
| `warning`             | `phase2:warn` | `slo-incident`, `severity:phase2-warn`, `needs-triage` |
| `info`                | `phase3:info` | `slo-incident`, `severity:phase3-info` |

## Acceptance criteria

- [x] `python scripts/slo_backlog.py --dry-run --prometheus-url http://127.0.0.1:9090` parses the sample alert payload without errors
- [x] Duplicate fingerprints are detected against `gh issue list --label slo-incident --state open`
- [x] The severity prefix matches the PTX-aligned names
- [ ] Workflow runs every 10 min via cron (CI verification)
- [ ] A test firing alert (Prometheus `POST /api/v1/alerts` with a stub payload) results in exactly one issue opened per fingerprint
- [ ] When the alert clears, the issue is auto-closed by a follow-up workflow (added in WP-14)

## How to trigger manually

```bash
gh workflow run slo-backlog.yml \
  -f prometheus_url=http://localhost:9090 \
  -f dry_run=false
```

Or in dry-run mode (no issue creation):

```bash
gh workflow run slo-backlog.yml -f dry_run=true
```