#!/bin/bash

# Set HOME if not set (needed for brew)
if [ -z "$HOME" ]; then
    export HOME="/Users/kooshapari"
    echo "Setting HOME to $HOME" >&2
fi

# Source the user profile to ensure Python is in the PATH
if [ -f "$HOME/.zprofile" ]; then
    source "$HOME/.zprofile"
    echo "Sourced $HOME/.zprofile" >&2
else
    echo "Warning: $HOME/.zprofile not found" >&2
fi

# Find the Python executable
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found in PATH" >&2
    echo "PATH: $PATH" >&2
    # Try direct paths as fallback
    if [ -f "/usr/bin/python3" ]; then
        PYTHON_CMD="/usr/bin/python3"
    elif [ -f "/usr/local/bin/python3" ]; then
        PYTHON_CMD="/usr/local/bin/python3"
    elif [ -f "/opt/homebrew/bin/python3" ]; then
        PYTHON_CMD="/opt/homebrew/bin/python3"
    else
        echo "Error: Could not find Python executable" >&2
        exit 1
    fi
fi

# Print debug information
echo "Using Python: $(which $PYTHON_CMD)" >&2
echo "Python version: $($PYTHON_CMD --version)" >&2
echo "Current directory: $(pwd)" >&2
echo "Arguments: $*" >&2

# Set MCP environment variables
export MCP_MODE="stdio"
export PYTHONUNBUFFERED=1

# Execute Python with the provided arguments and ensure it doesn't exit prematurely
# The 'exec' command replaces the current process with the Python process
# This ensures that signals are properly passed to the Python process
exec $PYTHON_CMD "$@"

# This code will never be reached due to the exec command above,
# but it's here as a fallback in case exec fails
echo "Error: Python process exited unexpectedly" >&2
exit 1
