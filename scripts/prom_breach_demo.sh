#!/usr/bin/env bash
# scripts/prom_breach_demo.sh — exercise the WP-13 → WP-19 closure loop.
#
# Brings up the local Prometheus + Grafana stack, pushes synthetic
# samples that exceed the cli_success_rate burn-rate alert, and
# waits for the slo-backlog.yml workflow to open a tracking issue.
#
# NOT FOR PRODUCTION. This script is for governance-loop smoke testing
# on developer machines.

set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-observability/docker-compose.yml}"
BREACH_TARGET="${BREACH_TARGET:-http://127.0.0.1:9090}"
BREACH_ERRORS="${BREACH_ERRORS:-250}"
BREACH_SUCCESSES="${BREACH_SUCCESSES:-500}"
WAIT_SECONDS="${WAIT_SECONDS:-60}"

echo "[breach-demo] starting local stack: $COMPOSE_FILE"
docker compose -f "$COMPOSE_FILE" up -d prometheus grafana

echo "[breach-demo] waiting for /metrics to be ready..."
for _ in $(seq 1 30); do
  if curl -fsS "$BREACH_TARGET/health" >/dev/null 2>&1; then
    echo "[breach-demo] server is up"
    break
  fi
  sleep 1
done

echo "[breach-demo] triggering synthetic breach: $BREACH_ERRORS errors, $BREACH_SUCCESSES successes"
cargo run -q -p phenotype-tooling-observability --bin breach-sim -- \
  --target "$BREACH_TARGET" \
  --error-count "$BREACH_ERRORS" \
  --success-count "$BREACH_SUCCESSES"

echo "[breach-demo] breach posted. waiting $WAIT_SECONDS seconds for Prometheus to scrape + alert"
sleep "$WAIT_SECONDS"

echo "[breach-demo] checking for slo:phase1:crit issues"
gh issue list --label slo:phase1:crit --state all --limit 5 || true

echo "[breach-demo] done. If no issue appeared, inspect .github/workflows/slo-backlog.yml + Prometheus rules."
