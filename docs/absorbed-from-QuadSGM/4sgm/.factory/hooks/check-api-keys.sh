#!/usr/bin/env bash
set -euo pipefail

# API Key Detection Hook
# Prevents hardcoded API keys in application code (CRITICAL SECURITY)

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
content=$(echo "$input" | jq -r '.tool_input.content')

# Skip test files, example files, and documentation
if echo "$file_path" | grep -qE '(tests/|.test.|.spec.|.example|README|.md$)'; then
  exit 0
fi

# Check for hardcoded API keys in app code
if echo "$content" | grep -qE '(sk-ant-|sk-[a-zA-Z0-9]{40,}|eyJ[a-zA-Z0-9_-]{20,})'; then
  if echo "$file_path" | grep -qE '(backend/|frontend/)'; then
    echo "❌ API key detected in application code: $file_path" >&2
    echo "" >&2
    echo "🚨 CRITICAL SECURITY VIOLATION:" >&2
    echo "API keys must NEVER be hardcoded in application code." >&2
    echo "" >&2
    echo "✅ Use environment variables instead:" >&2
    echo "   Python: os.getenv('ANTHROPIC_API_KEY')" >&2
    echo "   TypeScript: process.env.ANTHROPIC_API_KEY" >&2
    echo "" >&2
    echo "✅ Configure in .env file (never committed):" >&2
    echo "   ANTHROPIC_API_KEY=sk-ant-xxxxx" >&2
    exit 2  # Block
  fi
fi

exit 0
