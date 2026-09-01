#!/usr/bin/env bash
# Generic sidecar spawn script. Sourced from each plugin's plugin.env.
# Idempotent: no-op if the service is already up.
#
# Usage (called by forge plugin enable hook):
#   ./scripts/spawn.sh <plugin-name>
#
# Env expected (set by plugin.env):
#   PHENO_PLUGIN_NAME       — e.g., "pheno-supermemory"
#   PHENO_BINARY_PATH       — absolute path to the sidecar binary
#   PHENO_BINARY_ARGS       — space-separated args to pass to the binary
#   PHENO_STATE_DIR         — runtime state directory (e.g., /var/lib/pheno-forge/supermemory)
#   PHENO_HEALTH_URL        — health check URL (optional, for HTTP backends)
#   PHENO_HEALTH_CMD        — health check command (optional, for stdio backends)
#   PHENO_SD_UNIT           — systemd unit name (e.g., "pheno-supermemory.service")

set -euo pipefail

PLUGIN_NAME="${1:-${PHENO_PLUGIN_NAME}}"
if [[ -z "$PLUGIN_NAME" ]]; then
  echo "spawn.sh: PHENO_PLUGIN_NAME not set and no arg given" >&2
  exit 64
fi

# Find the plugin directory (so we can source plugin.env)
PLUGIN_DIR="${PHENO_PLUGIN_DIR:-$(dirname "$0")/../plugins/$PLUGIN_NAME}"
if [[ -f "$PLUGIN_DIR/plugin.env" ]]; then
  # shellcheck source=/dev/null
  source "$PLUGIN_DIR/plugin.env"
fi

# Linux: delegate to systemd (the canonical path)
if command -v systemctl >/dev/null 2>&1; then
  SD_UNIT="${PHENO_SD_UNIT:-pheno-${PLUGIN_NAME#pheno-}.service}"
  if systemctl is-active --quiet "$SD_UNIT"; then
    echo "spawn.sh: $SD_UNIT already active"
    exit 0
  fi
  sudo systemctl start "$SD_UNIT"
  echo "spawn.sh: $SD_UNIT started"
  exit 0
fi

# macOS / no-systemd: launch as a background process, log to PHENO_STATE_DIR/log
if [[ -z "${PHENO_BINARY_PATH:-}" ]]; then
  echo "spawn.sh: PHENO_BINARY_PATH not set" >&2
  exit 65
fi
mkdir -p "$PHENO_STATE_DIR"
LOG_FILE="$PHENO_STATE_DIR/${PLUGIN_NAME}.log"
PID_FILE="$PHENO_STATE_DIR/${PLUGIN_NAME}.pid"
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "spawn.sh: $PLUGIN_NAME already running (pid $(cat "$PID_FILE"))"
  exit 0
fi
# shellcheck disable=SC2086
nohup "$PHENO_BINARY_PATH" $PHENO_BINARY_ARGS >>"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "spawn.sh: $PLUGIN_NAME launched (pid $(cat "$PID_FILE"), log $LOG_FILE)"
