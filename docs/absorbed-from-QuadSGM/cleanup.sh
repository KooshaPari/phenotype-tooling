#!/usr/bin/env bash
set -euo pipefail

# 4SGM Codebase Cleanup Script
# Removes legacy and unnecessary files


echo "🧹 Cleaning up 4SGM codebase..."

# Keep only essential files
KEEP_FILES=(
    "README.md"
    "STARTUP.md"
    "FINAL_SETUP.md"
    "AGENTS.md"
    "CLAUDE.md"
)

# Remove legacy documentation from root
echo "📁 Cleaning root directory..."
cd 4sgm
for file in *.md; do
    skip=0
    for keep in "${KEEP_FILES[@]}"; do
        if [ "$file" = "$keep" ]; then
            skip=1
            break
        fi
    done
    if [ $skip -eq 0 ]; then
        echo "  ✗ Removing $file"
        rm -f "$file"
    fi
done

# Remove legacy documentation from 4sgm/
echo "📁 Cleaning 4sgm/ directory..."
cd 4sgm
rm -f *.md *.txt *.db 2>/dev/null || true
rm -rf *.egg-info 2>/dev/null || true

# Remove legacy backend files
echo "📁 Cleaning backend directory..."
cd backend
rm -f main.py fastapi_mcp_server.py mcp_server.py 2>/dev/null || true
rm -f mcp_client_wrapper.py 2>/dev/null || true
rm -f logging_config.py config.py 2>/dev/null || true
rm -f langgraph_*.py 2>/dev/null || true
rm -rf langgraph_* 2>/dev/null || true
rm -f test_advanced_features.py 2>/dev/null || true
rm -f requirements.txt 2>/dev/null || true

# Keep only essential backend files
echo "  ✓ Keeping: app.py, requirements_clean.txt, test_mcp_integration.py"

# Remove legacy API routes
cd ..
rm -rf api 2>/dev/null || true

# Remove legacy services
rm -rf services 2>/dev/null || true

# Remove legacy infrastructure
rm -rf infrastructure 2>/dev/null || true

# Remove legacy utils
rm -rf utils 2>/dev/null || true

# Remove legacy workflows
rm -rf langgraph_workflows 2>/dev/null || true

# Remove legacy memory
rm -rf langgraph_memory 2>/dev/null || true

# Remove legacy streaming
rm -rf langgraph_streaming 2>/dev/null || true

# Remove legacy recovery
rm -rf langgraph_recovery 2>/dev/null || true

# Remove legacy observability
rm -rf langgraph_observability 2>/dev/null || true

# Remove legacy tests
rm -f test_*.py 2>/dev/null || true

# Remove legacy scripts
cd ..
rm -f start_server.sh test_server.py 2>/dev/null || true

# Remove pytest cache
rm -rf .pytest_cache 2>/dev/null || true

# Remove __pycache__
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Remaining structure:"
echo "  4sgm/"
echo "  ├── cli.py"
echo "  ├── README.md"
echo "  ├── STARTUP.md"
echo "  ├── FINAL_SETUP.md"
echo "  ├── 4sgm/"
echo "  │   ├── backend/"
echo "  │   │   ├── app.py"
echo "  │   │   ├── requirements_clean.txt"
echo "  │   │   └── test_mcp_integration.py"
echo "  │   └── mcp_server/"
echo "  │       ├── server.py"
echo "  │       └── requirements.txt"
echo "  └── docker-compose.yml"
echo ""
