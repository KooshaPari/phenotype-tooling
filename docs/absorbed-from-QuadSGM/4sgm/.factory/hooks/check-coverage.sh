#!/usr/bin/env bash
set -euo pipefail

# Coverage Check Hook
# Verifies test coverage meets minimum thresholds

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

echo "📊 Checking test coverage for: $file_path"

# Backend Python coverage
if echo "$file_path" | grep -qE 'backend/.*\.py$'; then
  echo "Checking backend coverage..."
  cd backend

  # Activate virtual environment if exists
  if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
  fi

  # Run coverage check (90% threshold)
  pytest --cov=backend --cov-report=term-missing --cov-fail-under=90 tests/ || {
    echo "⚠️  Backend coverage below 90% threshold"
    echo "   Run: pytest --cov=backend --cov-report=html"
    echo "   Then open: htmlcov/index.html"
  }

  cd ..
fi

# Frontend TypeScript coverage
if echo "$file_path" | grep -qE 'frontend/.*\.(ts|tsx)$'; then
  echo "Checking frontend coverage..."
  cd frontend

  # Run coverage check (80% threshold)
  npm run test:coverage || {
    echo "⚠️  Frontend coverage below 80% threshold"
    echo "   Run: npm run test:coverage"
  }

  cd ..
fi

echo "✅ Coverage check complete"
exit 0
