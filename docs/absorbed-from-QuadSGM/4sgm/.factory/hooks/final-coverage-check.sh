#!/usr/bin/env bash
set -euo pipefail

# Final Coverage Check Hook
# Comprehensive coverage check at session end

echo "📊 Running final coverage check..."

# Backend coverage
echo "Checking backend coverage..."
cd backend

if [ -d ".venv" ]; then
  source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
fi

pytest --cov=backend --cov-report=term --cov-report=html tests/ || {
  echo "⚠️  Backend coverage check failed"
  echo "   Review htmlcov/index.html for details"
}

cd ..

# Frontend coverage
echo "Checking frontend coverage..."
cd frontend

npm run test:coverage || {
  echo "⚠️  Frontend coverage check failed"
  echo "   Review coverage/index.html for details"
}

cd ..

echo "✅ Final coverage check complete"
echo "   Backend: htmlcov/index.html"
echo "   Frontend: frontend/coverage/index.html"

exit 0
