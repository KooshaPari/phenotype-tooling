#!/usr/bin/env bash
set -euo pipefail

# Run Tests Hook
# Runs appropriate tests based on changed file

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

echo "🧪 Running tests for: $file_path"

# Backend Python tests
if echo "$file_path" | grep -qE 'backend/.*\.py$'; then
  echo "Running backend tests..."
  cd backend

  # Activate virtual environment if exists
  if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
  fi

  # Run tests for specific module if it exists
  module_name=$(basename "$file_path" .py)
  test_file="tests/test_${module_name}.py"

  if [ -f "$test_file" ]; then
    echo "Running specific tests: $test_file"
    pytest "$test_file" --tb=short -v || true
  else
    echo "Running all backend tests..."
    pytest tests/ --tb=short || true
  fi

  cd ..
fi

# Frontend TypeScript tests
if echo "$file_path" | grep -qE 'frontend/.*\.(ts|tsx)$'; then
  echo "Running frontend tests..."
  cd frontend

  # Run tests for specific component if it exists
  component_name=$(basename "$file_path" | sed 's/\.[^.]*$//')
  test_file="tests/${component_name}.test.tsx"

  if [ -f "$test_file" ]; then
    echo "Running specific tests: $test_file"
    npm run test -- "$test_file" || true
  else
    echo "Running all frontend tests..."
    npm run test || true
  fi

  cd ..
fi

echo "✅ Tests complete"
exit 0
