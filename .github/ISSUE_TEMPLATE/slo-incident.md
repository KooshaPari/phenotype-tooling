name: SLO Incident
description: Acknowledge + remediate an SLO breach detected by the burn-rate alerts.
title: "[slo:phase1:crit] "
labels: ["slo:phase1:crit", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        ## SLO breach detected

        This issue was opened automatically by `slo-backlog.yml`
        after a burn-rate alert fired in Prometheus.

        **Owner:** rotate on-call (see `#slo-oncall`)
        **Escalation:** Slack `#slo-incidents`
  - type: input
    id: slo_name
    attributes:
      label: SLO name
      description: Which SLO was breached? (from `observability/prometheus/phenotype-tooling.rules.yml`)
    validations:
      required: true
  - type: input
    id: burn_rate
    attributes:
      label: Burn rate (×)
      description: Multiplier over the steady-state error budget consumption.
    validations:
      required: true
  - type: input
    id: error_budget_remaining
    attributes:
      label: Error budget remaining (%)
      description: Percentage of monthly error budget still available.
  - type: textarea
    id: ack
    attributes:
      label: ACK comment
      description: On-call ack — what are you doing right now?
      placeholder: "Acked by @<you>. Paging secondary if not fixed by EOD. Primary remediation: ..."
    validations:
      required: true
  - type: textarea
    id: remediation
    attributes:
      label: Remediation plan
      description: What's the path to closing this issue?
      placeholder: |
        - [ ] Identify root cause via logs / metrics / traces
        - [ ] Land fix in `feat/<branch>` and PR against `main`
        - [ ] Re-run `slo-backlog.yml` to confirm budget recovers
        - [ ] Close issue when budget > 99% again
  - type: dropdown
    id: severity
    attributes:
      label: Severity tier
      options:
        - phase1:crit (5x burn, 30m)
        - phase2:warn (2x burn, 2h)
        - phase3:info (1.5x burn, 6h)
    validations:
      required: true