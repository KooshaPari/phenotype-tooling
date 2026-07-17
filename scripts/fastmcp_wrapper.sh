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

# Create a virtual environment if it doesn't exist
VENV_DIR="$HOME/.venv/fastmcp"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR" >&2
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Activate the virtual environment
# shellcheck disable=SC1090
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "Activated virtual environment at $VENV_DIR" >&2

    # Update PYTHON_CMD to use the Python from the virtual environment
    PYTHON_CMD="$VENV_DIR/bin/python"
    echo "Using Python from virtual environment: $PYTHON_CMD" >&2
else
    echo "Warning: Virtual environment activation script not found at $VENV_DIR/bin/activate" >&2
fi

# Check if FastMCP is installed
if ! $PYTHON_CMD -c "import fastmcp" &> /dev/null; then
    echo "Installing FastMCP..." >&2

    # Install FastMCP in the virtual environment
    $PYTHON_CMD -m pip install fastmcp
else
    echo "FastMCP is already installed" >&2
fi

# Execute command: run Python scripts via Python, otherwise pass through
case "$1" in
    *.py)
        exec "$PYTHON_CMD" "$@"
        ;;
    *)
        exec "$@"
        ;;
esac
