#!/bin/bash
# Launch script for the Agent Management System
# This script starts both the central agent server and the TUI

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up environment variables
export PYTHONPATH="$(dirname "$SCRIPT_DIR")"
export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1
export MCP_MODE=stdio
export HOME="$HOME"
export AGENT_REGISTRY_DB="$HOME/.agent_manager/agent_registry.db"

# Create the agent manager directory if it doesn't exist
mkdir -p "$HOME/.agent_manager"

# Start the TUI in a separate terminal window
echo "Starting Agent Manager TUI..."
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python agent_manager_tui.py\""

# Start the central agent server
echo "Starting Central Agent Server..."
"$SCRIPT_DIR/central_agent_server.py"
