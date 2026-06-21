#!/usr/bin/env bash
set -euo pipefail

# Environment Check Hook
# Verifies required environment variables are set at session start

echo "🔍 Checking environment variables..."

# Required environment variables
REQUIRED_VARS=(
  "ANTHROPIC_API_KEY"
  "OPENAI_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_KEY"
)

missing_vars=()

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
  echo "⚠️  Missing required environment variables:" >&2
  for var in "${missing_vars[@]}"; do
    echo "   • $var" >&2
  done
  echo "" >&2
  echo "   Set in backend/.env or export:" >&2
  echo "   export ANTHROPIC_API_KEY=sk-ant-xxxxx" >&2
  echo "   export OPENAI_API_KEY=sk-xxxxx" >&2
  echo "   export SUPABASE_URL=https://xxxxx.supabase.co" >&2
  echo "   export SUPABASE_KEY=eyJxxx..." >&2

  # Don't block, just warn
  exit 0
fi

echo "✅ All required environment variables are set"
exit 0
