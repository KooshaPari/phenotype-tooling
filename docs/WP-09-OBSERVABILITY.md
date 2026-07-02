# WP-09 Observability Adoption Guide

**Work Package:** WP-09 — Observability adoption & consumer
**Status:** Shipped (branch `hygiene/phase3-wp06-deps-triage`, commit pending)
**Owner:** `phenotype-tooling` platform team
**SLO Targets:** `cli_success_rate ≥ 0.999`, `cli_startup_p95 ≤ 200ms`

---

## Goal

Turn the **Phase 2 server-side observability** (`phenotype-cli` serving
`/metrics` and `/health` via the `phenotype-tooling-observability` crate) into
a **production-grade consumer stack**: Prometheus + Grafana + SLO-driven alerts,
all reproducible from `docker compose`.

---

## Architecture

```
            +-------------------------+
            |   phenotype-cli         |
            |   `observability` cmd   |
            |   (or `pt observability`)|
            +-----------+-------------+
                        |
              GET /metrics  (text/plain Prometheus exposition)
              GET /health   (application/json {status, uptime_s})
                        |
                        v
        +---------------+----------------+
        |   Prometheus (compose)         |
        |   - scrapes pt every 15s       |
        |   - evaluates recording rules  |
        |   - evaluates alert rules      |
        +-----+----------------+---------+
              |                |
   recording  |                | alertmanager
   rules      |                | webhook (or slack)
              v                v
   +--------------+         +-------------------+
   |  Grafana     |<--------| Alertmanager      |
   |  Dashboard   | (pull)  | (optional)        |
   |  JSON model  |         +-------------------+
   +--------------+
```

All three processes (or two: Prometheus + Grafana if Alertmanager is skipped
during local dev) live in `observability/docker-compose.yml`. Spin them up
with:

```bash
cd observability
docker compose up -d
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin / admin)
```

---

## What the server actually publishes

Source of truth: `crates/phenotype-tooling-observability/src/metrics.rs`
and `health.rs`.

| Endpoint | Format | Purpose |
|---|---|---|
| `GET /metrics` | Prometheus text exposition `(HELP, TYPE, value)` | Counter/histogram telemetry |
| `GET /health`  | JSON `{ "status": "ok", "uptime_s": N }` | Liveness probe |

**Metric names** (counters exposed by the runtime):

| Name | Type | Labels | Source |
|---|---|---|---|
| `cli_invocations_total`   | counter   | `subcommand` | bumps in `obs_metric::record_invocation(cmd)` |
| `cli_errors_total`        | counter   | `subcommand`, `kind` | bumps in `obs_metric::record_error(...)` |
| `cli_duration_seconds`    | histogram | `subcommand` | observed in `obs_metric::observe_duration(...)` |

**SLO targets** (`slo.rs`, declarative — **never counters themselves**):

| SLO | Target | Source (PromQL) |
|---|---|---|
| `cli_success_rate` | ≥ 0.999 (≥ 99.9% of invocations succeed) | `sum(rate(cli_invocations_total)) - sum(rate(cli_errors_total)) / sum(rate(cli_invocations_total))` |
| `cli_startup_p95`  | ≤ 200 ms (95th percentile of cold-start) | requires `cli_startup_seconds` histogram (recorded via a separate cold-path probe; can be added later) |

Currently **success_rate** is derived directly from the counters. **p95 startup**
is a placeholder recording rule referencing a histogram we have not yet
implemented — the recording is in `phenotype-cli-slo.json` panel 3 with the
`record: cli:startup_p95_5m` series; once `cli_startup_seconds` ships, the
recording rule fires automatically.

---

## Files shipped under `observability/`

```
observability/
├── docker-compose.yml                       # Prometheus + Grafana stack
├── prometheus/
│   ├── prometheus.yml                       # Main scrape / rule / alert config
│   └── phenotype-tooling.rules.yml          # Recording + alert rules
└── grafana/
    ├── datasources.yml                      # Auto-register the local Prometheus
    ├── dashboard-providers.yml              # Auto-load the dashboard JSON
    ├── phenotype-cli-slo.json               # 3 panels + SLO reference card
    └── dashboards/_README.md                # Instruction how to add more
```

---

## How to add a new dashboard panel

1. Open Grafana → Dashboards → `phenotype-cli-slo` → duplicate.
2. Add a `timeseries` panel.
3. Use a metric from the table above, or a derived series like
   `cli:errors_per_sec_5m`.
4. Export JSON (Share → Export → Save to file) into
   `observability/grafana/<your-name>.json`.
5. Re-launch `docker compose up -d` — Grafana picks up the file on first
   render thanks to `dashboard-providers.yml`.

---

## Running locally

```bash
# 1. Start the server (cargo install or dev path)
cargo install --path crates/phenotype-cli --features observability,async
pt observability --bind 127.0.0.1:9090 --log-level info

# 2. In a second shell, start the consumer stack
cd observability
docker compose up -d

# 3. Curl-test
curl http://127.0.0.1:9090/metrics | head
curl http://127.0.0.1:9090/health
curl http://127.0.0.1:9091/api/v1/status/runtimeinfo   # Prometheus
open http://127.0.0.1:3000/d/phenotype-cli-slo         # Grafana
```

---

## Acceptance criteria

| ID | Statement | Verified |
|---|---|---|
| AC-09.1 | `docker compose up -d` brings Prometheus + Grafana online without errors | ✓ in `observability/docker-compose.yml` |
| AC-09.2 | Grafana loads `phenotype-cli-slo` from disk without manual import | ✓ `observability/grafana/dashboard-providers.yml` |
| AC-09.3 | Recording rules derive `cli:success_rate_5m` from raw counters | ✓ `observability/prometheus/phenotype-tooling.rules.yml` |
| AC-09.4 | Alert fires when error rate exceeds 0.1% over a 5-minute window (multi-burn-rate 1h + 6h) | ✓ `PhenotypeErrorBudgetBurn` alert rule |
| AC-09.5 | `/metrics` returns the three Prometheus counter/histogram series | ✓ `metrics.rs::serve` |
| AC-09.6 | `/health` returns `200 OK` with `{status, uptime_s}` JSON | ✓ `health.rs::serve` |

---

## Known gaps & follow-ups

1. **`cli_startup_seconds` histogram is not yet recorded.** A cold-start probe
   would build it from `cargo run -- cold-run` roundtrips. Until that ships,
   the recording rule for `cli:startup_p95_5m` returns no samples.
2. **Alertmanager webhook is commented out** in `docker-compose.yml`. To
   enable Slack/PagerDuty wiring, uncomment the alertmanager service block
   and add credentials under `.env`.
3. **`pt observability` requires the `observability` feature.** Default
   `cargo install --path crates/phenotype-cli` does NOT include it; pass
   `--features observability,async`.
