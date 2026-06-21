#!/usr/bin/env bash
set -euo pipefail

# 4SGM Local Development Setup Script
# This script initializes all required services for local development

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm"
PG_DATA_DIR="${HOME}/Library/PostgreSQL/15/data"
PG_USER="user"
PG_PASSWORD="password"
PG_DB="4sgm"
PG_PORT="5432"

echo -e "${BLUE}"
echo "================================================"
echo "  4SGM Local Development Setup"
echo "================================================"
echo -e "${NC}"

# ============================================
# Check Prerequisites
# ============================================

echo ""
echo "📋 Checking prerequisites..."
echo ""

# Python 3
echo -n "  Checking Python 3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    echo "    Install with: brew install python@3.10"
    exit 1
fi

# PostgreSQL
echo -n "  Checking PostgreSQL... "
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version 2>&1 | awk '{print $3}')
    echo -e "${GREEN}✓ Found: $PG_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
    echo "    Install with: brew install postgresql@15"
    echo ""
    read -p "  Would you like to install PostgreSQL now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install postgresql@15
    else
        echo -e "${RED}✗ PostgreSQL is required${NC}"
        exit 1
    fi
fi

# Redis
echo -n "  Checking Redis... "
if command -v redis-cli &> /dev/null; then
    REDIS_VERSION=$(redis-server --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Found: $REDIS_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
    echo "    Install with: brew install redis"
    echo ""
    read -p "  Would you like to install Redis now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install redis
    else
        echo -e "${RED}✗ Redis is required${NC}"
        exit 1
    fi
fi

# ============================================
# PostgreSQL Setup
# ============================================

echo ""
echo "🗄️  Setting up PostgreSQL..."
echo ""

# Check if PostgreSQL data directory exists
if [ ! -d "$PG_DATA_DIR" ]; then
    echo -n "  Initializing data directory... "
    mkdir -p "$PG_DATA_DIR"
    initdb -D "$PG_DATA_DIR" --username=postgres > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "    Try running: initdb -D $PG_DATA_DIR --username=postgres"
        exit 1
    fi
else
    echo "  Data directory already exists"
fi

# Start PostgreSQL
echo -n "  Starting PostgreSQL... "
if pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Already running${NC}"
else
    pg_ctl -D "$PG_DATA_DIR" start > /dev/null 2>&1
    sleep 2
    if pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "    Try running: pg_ctl -D $PG_DATA_DIR start"
        exit 1
    fi
fi

# Create user if not exists
echo -n "  Creating database user '$PG_USER'... "
if psql -U postgres -tAc "SELECT 1 FROM pg_user WHERE usename = '$PG_USER'" | grep -q 1; then
    echo -e "${GREEN}✓ Already exists${NC}"
else
    psql -U postgres -c "CREATE USER $PG_USER WITH PASSWORD '$PG_PASSWORD' CREATEDB;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "    Try running: psql -U postgres -c \"CREATE USER $PG_USER WITH PASSWORD '$PG_PASSWORD' CREATEDB;\""
    fi
fi

# Create database if not exists
echo -n "  Creating database '$PG_DB'... "
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "$PG_DB"; then
    echo -e "${GREEN}✓ Already exists${NC}"
else
    psql -U postgres -c "CREATE DATABASE $PG_DB OWNER $PG_USER;" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "    Try running: psql -U postgres -c \"CREATE DATABASE $PG_DB OWNER $PG_USER;\""
    fi
fi

# ============================================
# Redis Setup
# ============================================

echo ""
echo "⚡ Setting up Redis..."
echo ""

echo -n "  Starting Redis... "
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Already running${NC}"
else
    redis-server --daemonize yes --port 6379 > /dev/null 2>&1
    sleep 1
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "    Try running: redis-server"
    fi
fi

# ============================================
# Python Environment
# ============================================

echo ""
echo "🐍 Setting up Python environment..."
echo ""

cd "$PROJECT_ROOT"

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo -n "  Creating virtual environment... "
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC}"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo -n "  Upgrading pip... "
pip install --quiet --upgrade pip setuptools wheel
echo -e "${GREEN}✓${NC}"

# Install uv
echo -n "  Installing uv package manager... "
pip install --quiet uv
echo -e "${GREEN}✓${NC}"

# Install project dependencies
echo -n "  Installing project dependencies... "
uv pip install -e . --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "    Try running: uv pip install -e ."
    exit 1
fi

# ============================================
# Environment Configuration
# ============================================

echo ""
echo "⚙️  Configuring environment..."
echo ""

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ Created .env from template${NC}"
        echo "  Please update .env with your API keys:"
        echo "    - OPENAI_API_KEY"
        echo "    - SUPABASE_URL"
        echo "    - SUPABASE_KEY"
    fi
else
    echo "  .env already exists"
fi

# Create logs directory
mkdir -p logs
echo "  Created logs directory"

# ============================================
# Verification
# ============================================

echo ""
echo "✅ Verification..."
echo ""

echo -n "  PostgreSQL (pg_isready): "
if pg_isready -U "$PG_USER" -d "$PG_DB" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "  Redis (redis-cli ping): "
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "  Python modules: "
if python3 -c "import fastapi, langchain, fastmcp" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "    Try running: uv pip install -e ."
fi

# ============================================
# Summary
# ============================================

echo ""
echo -e "${GREEN}================================================"
echo "  ✅ Setup Complete!"
echo "================================================${NC}"
echo ""
echo "📝 Next steps:"
echo ""
echo "  1. Update .env with your API keys:"
echo "     nano .env"
echo ""
echo "  2. Start all services:"
echo "     make start"
echo "     or"
echo "     process-compose up"
echo ""
echo "  3. Open FastAPI docs:"
echo "     open http://localhost:8000/docs"
echo ""
echo "  4. Run tests:"
echo "     make test"
echo ""
echo "🛠️  Development tools:"
echo "     make help        - Show all available commands"
echo "     make health      - Check service health"
echo "     make logs        - View service logs"
echo ""
