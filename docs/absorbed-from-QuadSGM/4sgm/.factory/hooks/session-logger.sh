#!/usr/bin/env bash
set -euo pipefail

# Session Logger Hook
# Logs session start/end for tracking and analytics

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
LOG_DIR=".factory/logs"
LOG_FILE="$LOG_DIR/sessions.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Get session info from environment or input
SESSION_TYPE="${FACTORY_SESSION_TYPE:-unknown}"
SESSION_ID="${FACTORY_SESSION_ID:-$(date +%s)}"

# Log entry
echo "[$TIMESTAMP] Session $SESSION_TYPE - ID: $SESSION_ID" >> "$LOG_FILE"

# Also log to stdout for debugging
echo "📝 Session logged: $SESSION_TYPE (ID: $SESSION_ID)"

exit 0
