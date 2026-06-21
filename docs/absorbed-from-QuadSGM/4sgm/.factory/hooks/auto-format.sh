#!/usr/bin/env bash
set -euo pipefail

# Auto-Format Hook
# Automatically formats Python and TypeScript files

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Format Python files
if echo "$file_path" | grep -qE '\.py$'; then
  if [ -f "$file_path" ]; then
    echo "🔧 Formatting Python file: $file_path"
    cd backend 2>/dev/null || cd .
    ruff format "$file_path" 2>/dev/null || true
    echo "✅ Python formatting complete"
  fi
fi

# Format TypeScript/JavaScript files
if echo "$file_path" | grep -qE '\.(ts|tsx|js|jsx)$'; then
  if [ -f "$file_path" ]; then
    echo "🔧 Formatting TypeScript file: $file_path"
    cd frontend 2>/dev/null || cd .
    npx prettier --write "$file_path" 2>/dev/null || true
    echo "✅ TypeScript formatting complete"
  fi
fi

exit 0
