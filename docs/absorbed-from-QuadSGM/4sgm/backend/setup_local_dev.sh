#!/usr/bin/env bash
set -euo pipefail
# Setup script for local development configuration

echo "=== 4SGM Chatbot Local Development Setup ==="
echo ""
echo "This script sets up the environment for local development."
echo "Expected configuration:"
echo "- LLM: localhost:8317 proxy -> claude-haiku-4-5-20251001"
echo "- Embeddings: OpenRouter -> Gemini"
echo "- Backend: http://localhost:8000"
echo ""

# Create .env file for local development if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file for local development..."
    cat > .env << EOF
# 4SGM Chatbot Local Development Configuration
STAGE=local

# LLM Configuration - Using local proxy
ANTHROPIC_API_KEY=dummy-not-used
ANTHROPIC_BASE_URL=http://localhost:8317
CLAUDE_MODEL=claude-haiku-4-5-20251001

# Embeddings - OpenRouter + Gemini
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_MODEL=google/gemini-embedding-001
EMBEDDING_DIMENSIONS=768

# Supabase (leave empty for mock mode)
SUPABASE_URL=
SUPABASE_KEY=

# API Configuration
API_BASE_URL=http://localhost:8000
EOF
    echo "✓ Created .env file"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "To start the backend server:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Important: Make sure you have a proxy running at localhost:8317"
echo "This is typically handled by the 4SGM CLI tool with:"
echo "  4sgm start local"
echo ""
