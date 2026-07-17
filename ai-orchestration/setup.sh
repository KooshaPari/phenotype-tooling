#!/bin/bash

# Install required packages
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example. Please update it with your API keys."
fi

echo "Setup complete. You can now run the application with 'python app.py'."
