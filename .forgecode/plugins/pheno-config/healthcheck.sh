#!/usr/bin/env bash
# Generic sidecar healthcheck script. Returns 0 + JSON status on success.
#
# Usage (called by forge session boot hook):
#   ./scripts/healthcheck.sh <plugin-name>
#
# Output (stdout, JSON):
#   {"plugin":"<name>","status":"healthy|unhealthy","detail":"...","uptime_s":N}
#
# Env expected (set by plugin.env):
#   PHENO_PLUGIN_NAME       — e.g., "pheno-supermemory"
#   PHENO_HEALTH_URL        — health check URL (for HTTP backends)
#   PHENO_HEALTH_CMD        — health check command (for stdio backends)
#   PHENO_HEALTH_TIMEOUT    — timeout in seconds (default: 5)

set -euo pipefail

PLUGIN_NAME="${1:-${PHENO_PLUGIN_NAME}}"
if [[ -z "$PLUGIN_NAME" ]]; then
  echo '{"status":"error","detail":"PHENO_PLUGIN_NAME not set"}'
  exit 64
fi

PLUGIN_DIR="${PHENO_PLUGIN_DIR:-$(dirname "$0")/../plugins/$PLUGIN_NAME}"
if [[ -f "$PLUGIN_DIR/plugin.env" ]]; then
  # shellcheck source=/dev/null
  source "$PLUGIN_DIR/plugin.env"
fi

TIMEOUT="${PHENO_HEALTH_TIMEOUT:-5}"

# HTTP backend healthcheck
if [[ -n "${PHENO_HEALTH_URL:-}" ]]; then
  if command -v curl >/dev/null 2>&1; then
    HTTP_CODE=$(curl -fsS -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$PHENO_HEALTH_URL" 2>/dev/null || echo "000")
    if [[ "$HTTP_CODE" =~ ^2 ]]; then
      printf '{"plugin":"%s","status":"healthy","detail":"HTTP %s","url":"%s"}\n' \
        "$PLUGIN_NAME" "$HTTP_CODE" "$PHENO_HEALTH_URL"
      exit 0
    fi
    printf '{"plugin":"%s","status":"unhealthy","detail":"HTTP %s","url":"%s"}\n' \
      "$PLUGIN_NAME" "$HTTP_CODE" "$PHENO_HEALTH_URL"
    exit 1
  fi
fi

# stdio backend healthcheck (e.g., cognee-mcp)
if [[ -n "${PHENO_HEALTH_CMD:-}" ]]; then
  if timeout "$TIMEOUT" bash -c "$PHENO_HEALTH_CMD" >/dev/null 2>&1; then
    printf '{"plugin":"%s","status":"healthy","detail":"stdio check passed"}\n' "$PLUGIN_NAME"
    exit 0
  fi
  printf '{"plugin":"%s","status":"unhealthy","detail":"stdio check failed"}\n' "$PLUGIN_NAME"
  exit 1
fi

# Fallback: just check that the process is running
SD_UNIT="${PHENO_SD_UNIT:-pheno-${PLUGIN_NAME#pheno-}.service}"
if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet "$SD_UNIT"; then
  printf '{"plugin":"%s","status":"healthy","detail":"systemd unit active"}\n' "$PLUGIN_NAME"
  exit 0
fi

PID_FILE="${PHENO_STATE_DIR:-/tmp/pheno-forge}/${PLUGIN_NAME}.pid"
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  printf '{"plugin":"%s","status":"healthy","detail":"process running (pid %s)"}\n' \
    "$PLUGIN_NAME" "$(cat "$PID_FILE")"
  exit 0
fi

printf '{"plugin":"%s","status":"unhealthy","detail":"no healthcheck defined and no process found"}\n' "$PLUGIN_NAME"
exit 1
