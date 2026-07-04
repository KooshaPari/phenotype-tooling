# WP-19 — Synthetic SLO Breach → Issue → On-call Ack → Post-mortem Closure Proof

## Purpose

Demonstrate the **end-to-end governance loop** for the
`phenotype-tooling` ecosystem: when something breaks the SLO, the
infrastructure detects it, opens an issue, the on-call acks, and
a post-mortem commit closes the loop. This WP is not about
production alerts — it's about **proving the loop closes** so we
trust the rest of the governance surface.

## Architecture

```
   breach-sim (this WP)         slo-backlog.yml (WP-13)        on-call ack workflow
   ─────────────────────        ────────────────────────        ──────────────────────
   ┌───────────────────┐        ┌──────────────────────┐        ┌──────────────────┐
   │ POST samples      │ ──────▶│ eval burn-rate        │───────▶│opens GH issue    │
   │ to /metrics       │        │ from rules.yml        │        │[slo:phase1:crit] │
   │ (errors > tol.)  │        │ → PHENOTYPE-1 fires   │        │                  │
   └───────────────────┘        └──────────────────────┘        └──────────────────┘
                                                                            │
                                                                 ┌──────────┴──────────┐
                                                                 ▼                     ▼
                                                       incident-postmortem.yml    issue closes when
                                                       opens PR with root-cause  PR merges to main
                                                       analysis + remediation
```

## Files Added

| Path | Purpose |
|---|---|
| `crates/phenotype-tooling-observability/src/bin/breach_sim.rs` | Synthetic breach generator (uploads to `/metrics`) |
| `scripts/prom_breach_demo.sh` | One-shot: bring up stack → trigger breach → wait for issue |
| `.github/workflows/slo-incident.yml` | On-call ack workflow: opens issue on `PHENOTYPE-1` alert (closes the loop with WP-13) |
| `.github/ISSUE_TEMPLATE/slo-incident.md` | Issue template for ack + remediation tracking |
| `.github/workflows/incident-postmortem.yml` | Generates post-mortem PR with root-cause analysis template |
| `docs/WP-19-SLO-CLOSURE.md` | This document |

## Verification: How to Run It

```bash
# 1. Bring up local Prometheus + Grafana stack
docker compose -f observability/docker-compose.yml up -d

# 2. Start the observability server (in another shell)
cargo run -p phenotype-tooling-observability --bin observability \
    --target-port 9090

# 3. Run the breach generator
cargo run -p phenotype-tooling-observability --bin breach-sim -- \
    --target http://127.0.0.1:9090 \
    --error-count 250 \
    --success-count 500

# 4. Wait ~30s for Prometheus to scrape + alert manager to evaluate

# 5. Check .github issues for `slo:phase1:crit cli_success_rate burn`
gh issue list --label slo:phase1:crit

# 6. The matching workflow should have:
#    - opened the issue
#    - assigned it to @maintainers
#    - published a chart of the burn rate on the issue

# 7. ACK the issue (any comment counts) and a postmortem PR is opened

# 8. Verify the loop: gh pr list --label postmortem
```

Expected outcome:
- 1 issue opened within 1 minute of breach (`slo:phase1:crit` label)
- 1 PR opened within 5 minutes of ACK (`postmortem` label)
- 1 commit on `main` once the PR merges — that commit is the
  **closure proof** that the governance loop ran end-to-end.

## Acceptance Criteria

1. `breach-sim` exits 0 with the breach posted to `/metrics`
2. Within 60s the issue is filed with the `slo:phase1:crit` label
3. Within 5 minutes of any ACK comment, a `postmortem` PR exists
4. The post-mortem PR template includes: timeline, root cause,
   remediation action items, and "yes/no: re-occurrence likelihood"
5. Merging the postmortem PR triggers a new run of `coverage.yml`
   and `mutation.yml` against the patched code — proving the
   feedback loop includes verification

## Why this WP matters

Without WP-19, the alert → issue → ack → post-mortem pipeline
**looks** correct but has never been exercised end-to-end. WP-19 is
the smoke test for the entire governance surface.

If the issue doesn't appear, we know **before** a real breach that
the loop is broken — which is the entire point of governance.
