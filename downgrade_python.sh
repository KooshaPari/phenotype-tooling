#!/bin/bash
# Script to downgrade Python to a compatible version and run the API server

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "pyenv is not installed. Please install pyenv first."
    exit 1
fi

# Install Python 3.11.7 if not already installed
if ! pyenv versions | grep -q "3.11.7"; then
    echo "Installing Python 3.11.7..."
    pyenv install 3.11.7
fi

# Set local Python version to 3.11.7
echo "Setting local Python version to 3.11.7..."
pyenv local 3.11.7

# Verify Python version
echo "Python version:"
python --version

# Run the API server
echo "Starting API server..."
python run_api.py
