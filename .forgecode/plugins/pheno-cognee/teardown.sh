#!/usr/bin/env bash
# Generic sidecar teardown script. Stops the systemd unit (Linux) or kills the
# background process (macOS). Idempotent.
#
# Usage (called by forge plugin disable hook):
#   ./scripts/teardown.sh <plugin-name>

set -euo pipefail

PLUGIN_NAME="${1:-${PHENO_PLUGIN_NAME}}"
if [[ -z "$PLUGIN_NAME" ]]; then
  echo "teardown.sh: PHENO_PLUGIN_NAME not set and no arg given" >&2
  exit 64
fi

PLUGIN_DIR="${PHENO_PLUGIN_DIR:-$(dirname "$0")/../plugins/$PLUGIN_NAME}"
if [[ -f "$PLUGIN_DIR/plugin.env" ]]; then
  # shellcheck source=/dev/null
  source "$PLUGIN_DIR/plugin.env"
fi

if command -v systemctl >/dev/null 2>&1; then
  SD_UNIT="${PHENO_SD_UNIT:-pheno-${PLUGIN_NAME#pheno-}.service}"
  if ! systemctl is-active --quiet "$SD_UNIT"; then
    echo "teardown.sh: $SD_UNIT not active"
    exit 0
  fi
  sudo systemctl stop "$SD_UNIT"
  echo "teardown.sh: $SD_UNIT stopped"
  exit 0
fi

# macOS / no-systemd
PID_FILE="${PHENO_STATE_DIR:-/tmp/pheno-forge}/${PLUGIN_NAME}.pid"
if [[ ! -f "$PID_FILE" ]]; then
  echo "teardown.sh: $PLUGIN_NAME not running (no pid file)"
  exit 0
fi
PID="$(cat "$PID_FILE")"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID" || true
  sleep 2
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" || true
  fi
fi
rm -f "$PID_FILE"
echo "teardown.sh: $PLUGIN_NAME stopped"
