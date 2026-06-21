# 4SGM Native Process Orchestration - Implementation Plan

**Date**: January 31, 2026
**Phase**: Implementation & Execution
**Timeline**: 2-3 days for full implementation and testing

---

## 1. Implementation Roadmap

### Phase 1: Foundation (Day 1 AM)
- Install and verify native dependencies
- Create Brewfile
- Create setup scripts
- Validate environment

### Phase 2: Process Orchestration (Day 1 PM)
- Create process-compose.yaml
- Configure health checks
- Set up logging infrastructure
- Test service startup order

### Phase 3: API Gateway (Day 2 AM)
- Create Caddyfile
- Configure reverse proxy
- Set up development routing
- Test API access patterns

### Phase 4: Development Tooling (Day 2 PM)
- Create Makefile
- Create CLI wrapper scripts
- Configure IDE integration
- Validate full workflow

### Phase 5: Testing & Documentation (Day 3)
- End-to-end testing
- Failure scenario testing
- Performance benchmarking
- Documentation completion

---

## 2. Detailed Implementation Steps

### Step 1: Create Brewfile

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/Brewfile`

**Actions**:
1. List all system dependencies
2. Specify exact versions where possible
3. Include optional development tools
4. Add fallback alternatives

**Contents**:

```ruby
# Brewfile - 4SGM Development Dependencies

# Core Databases
brew "postgresql@15"
brew "redis"

# Web Server & Reverse Proxy
brew "caddy"

# Python Environment
brew "python@3.10"
brew "uv"

# CLI Tools
brew "just"  # Task runner
brew "direnv"  # Environment management

# Development & Debugging
brew "watchman"  # File watcher
brew "curl"  # HTTP client
brew "jq"  # JSON parser

# System Monitoring
brew "btop"  # Better top
brew "lnav"  # Log navigator

# Optional: GUI Tools
cask "pgadmin4"  # PostgreSQL admin
cask "redis-pro"  # Redis client
cask "postico2"  # PostgreSQL client (paid)

# Taps for additional packages
tap "homebrew-community/core"
tap "F1bonacc1/process-compose"

# Process Orchestrator
brew "F1bonacc1/process-compose/process-compose"
```

**Installation Command**:
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm
brew bundle
```

### Step 2: Environment Setup Script

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/scripts/setup-local-dev.sh`

**Actions**:
1. Check for required tools
2. Initialize PostgreSQL if needed
3. Set up data directory
4. Create initial database
5. Validate all connections

**Script**:

```bash
#!/bin/bash
set -e

echo "🚀 4SGM Local Development Setup"
echo "================================="
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"

# PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL not found${NC}"
    echo "  Install with: brew install postgresql@15"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL found: $(psql --version)${NC}"

# Redis
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}⚠ Redis not found${NC}"
    echo "  Install with: brew install redis"
    exit 1
fi
echo -e "${GREEN}✓ Redis found$(NC}"

# Check PostgreSQL data directory
echo ""
echo "🗄️  Configuring PostgreSQL..."

PG_DATA_DIR="${HOME}/Library/PostgreSQL/15/data"
if [ ! -d "$PG_DATA_DIR" ]; then
    echo "  Creating PostgreSQL data directory..."
    mkdir -p "$PG_DATA_DIR"
    initdb -D "$PG_DATA_DIR" --username=postgres
    echo -e "${GREEN}✓ PostgreSQL data directory initialized${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL data directory exists${NC}"
fi

# Start PostgreSQL if not running
echo ""
echo "🔧 Starting PostgreSQL..."
if pg_isready -U user &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL already running${NC}"
else
    pg_ctl -D "$PG_DATA_DIR" start
    sleep 2
    echo -e "${GREEN}✓ PostgreSQL started${NC}"
fi

# Create user and database if needed
echo ""
echo "📊 Setting up database..."
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "user"; then
    echo -e "${GREEN}✓ Database user exists${NC}"
else
    createuser -U postgres user -P user 2>/dev/null || true
    echo -e "${GREEN}✓ Database user created${NC}"
fi

if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "4sgm"; then
    echo -e "${GREEN}✓ Database '4sgm' exists${NC}"
else
    createdb -U postgres -O user 4sgm
    echo -e "${GREEN}✓ Database '4sgm' created${NC}"
fi

# Start Redis if not running
echo ""
echo "⚡ Starting Redis..."
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis already running${NC}"
else
    redis-server --daemonize yes
    sleep 1
    echo -e "${GREEN}✓ Redis started${NC}"
fi

# Set up Python environment
echo ""
echo "🐍 Setting up Python environment..."
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

source .venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q uv
uv pip install -e .
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

# Copy .env if needed
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ Created .env from template - update with secrets${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Update .env with your secrets"
echo "  2. Run: process-compose up"
echo "  3. Open: http://localhost:8000/docs"
```

### Step 3: Create process-compose.yaml

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/process-compose.yaml`

**Key Configuration**:

```yaml
version: "3.0"

environment:
  - LOG_DIR=logs
  - PYTHONUNBUFFERED=1
  - PYTHONPATH=/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm

processes:
  # ============================================
  # PHASE 1: Infrastructure (No Dependencies)
  # ============================================

  postgres:
    command: pg_ctl -D ${HOME}/Library/PostgreSQL/15/data start -w
    working_dir: .
    is_daemon: false

    env:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=4sgm

    startup:
      type: notify
      action: wait
      timeout: 10s

    shutdown:
      timeout: 5s
      signal: TERM

    restart_policy:
      backoff: exponential
      max_restarts: 3
      wait_period: 2s

    health:
      exec:
        command: pg_isready -U user -d 4sgm
      initial_delay: 2s
      period: 5s
      timeout: 3s

    log_configuration:
      no_colors: false
      mode: mixed
      location: logs/postgres.log

  redis:
    command: redis-server --port 6379 --loglevel notice
    working_dir: .

    startup:
      type: notify
      action: wait
      timeout: 5s

    shutdown:
      timeout: 3s
      signal: TERM

    restart_policy:
      backoff: exponential
      max_restarts: 3
      wait_period: 1s

    health:
      exec:
        command: redis-cli ping
      initial_delay: 1s
      period: 5s
      timeout: 2s

    log_configuration:
      no_colors: false
      mode: mixed
      location: logs/redis.log

  # ============================================
  # PHASE 2: MCP Server (Depends on Infra)
  # ============================================

  mcp_server:
    command: python -m fastmcp run mcp_server.server:mcp
    working_dir: /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm

    env_file: ../.env

    depends_on:
      postgres: running_ok
      redis: running_ok

    startup:
      type: notify
      action: wait
      timeout: 10s

    shutdown:
      timeout: 3s
      signal: TERM

    restart_policy:
      backoff: exponential
      max_restarts: 5
      wait_period: 2s

    log_configuration:
      no_colors: false
      mode: mixed
      location: ../logs/mcp_server.log

  # ============================================
  # PHASE 3: FastAPI Backend (Depends on MCP)
  # ============================================

  fastapi:
    command: python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
    working_dir: /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm

    env_file: ../.env

    depends_on:
      mcp_server: running_ok
      postgres: running_ok
      redis: running_ok

    startup:
      type: notify
      action: wait
      timeout: 15s

    shutdown:
      timeout: 5s
      signal: TERM

    restart_policy:
      backoff: exponential
      max_restarts: 5
      wait_period: 2s

    health:
      exec:
        command: curl -f http://localhost:8000/health || exit 1
      initial_delay: 3s
      period: 10s
      timeout: 5s

    log_configuration:
      no_colors: false
      mode: mixed
      location: ../logs/fastapi.log

log_configuration:
  location: logs/orchestrator.log
  level: info
```

### Step 4: Create Caddyfile

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/Caddyfile`

**Configuration**:

```caddyfile
# Development environment on port 9000
localhost:9000 {
    # API routes
    handle /api/* {
        uri strip_prefix /api
        reverse_proxy localhost:8000 {
            header_up X-Forwarded-For {http.request.remote}
            header_up X-Forwarded-Proto {http.request.proto}
        }
    }

    # Health check endpoint
    handle /health {
        reverse_proxy localhost:8000
    }

    # Swagger documentation
    handle /docs {
        reverse_proxy localhost:8000
    }

    # ReDoc documentation
    handle /redoc {
        reverse_proxy localhost:8000
    }

    # OpenAPI schema
    handle /openapi.json {
        reverse_proxy localhost:8000
    }

    # Frontend with fallback
    handle {
        reverse_proxy localhost:3001 {
            policy random_choose
        }
    }

    # Logging
    log {
        output file logs/caddy.log {
            roll_size 100mb
            roll_keep 5
            roll_keep_for 720h
        }
        level info
    }
}

# Production-like on port 9001 (single API)
localhost:9001 {
    reverse_proxy localhost:8000 {
        header_up X-Forwarded-For {http.request.remote}
        header_up X-Forwarded-Proto {http.request.proto}
    }

    log {
        output file logs/caddy-prod.log {
            roll_size 100mb
            roll_keep 5
        }
        level warn
    }
}
```

### Step 5: Create Makefile

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/Makefile`

**Structure**:

```makefile
.PHONY: help setup clean start stop logs restart health \
        postgres redis mcp api frontend test lint format \
        docker-start docker-stop database-init

# Default target
help:
	@echo "4SGM Development Commands"
	@echo "========================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup           - Initial setup (install deps, init DB)"
	@echo "  make clean           - Clean all artifacts and caches"
	@echo ""
	@echo "Service Management:"
	@echo "  make start           - Start all services via process-compose"
	@echo "  make stop            - Stop all services gracefully"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - Tail all service logs"
	@echo "  make health          - Check service health"
	@echo ""
	@echo "Individual Services:"
	@echo "  make postgres        - Start PostgreSQL only"
	@echo "  make redis           - Start Redis only"
	@echo "  make mcp             - Start MCP server only"
	@echo "  make api             - Start FastAPI only"
	@echo "  make frontend        - Start React frontend only"
	@echo ""
	@echo "Development:"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linting checks"
	@echo "  make format          - Format code"
	@echo "  make database-init   - Initialize database"
	@echo ""
	@echo "Docker Fallback:"
	@echo "  make docker-start    - Start services via Docker Compose"
	@echo "  make docker-stop     - Stop Docker services"
	@echo ""

# ====================================
# Setup & Installation
# ====================================

setup: .env
	@echo "🚀 Setting up 4SGM development environment..."
	@bash scripts/setup-local-dev.sh
	@echo "✅ Setup complete!"

.env:
	@if [ -f ".env.example" ]; then \
		cp .env.example .env; \
		echo "Created .env from template - update with your secrets"; \
	fi

clean:
	@echo "🧹 Cleaning..."
	rm -rf logs
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	@echo "✅ Cleaned!"

# ====================================
# Service Management
# ====================================

start:
	@echo "🚀 Starting 4SGM services..."
	process-compose up

stop:
	@echo "🛑 Stopping services..."
	process-compose down

restart: stop start

logs:
	@echo "📋 Tailing service logs..."
	process-compose logs -f

health:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "PostgreSQL:"
	@pg_isready -U user -d 4sgm && echo "  ✓ Running" || echo "  ✗ Not responding"
	@echo ""
	@echo "Redis:"
	@redis-cli ping && echo "  ✓ Running" || echo "  ✗ Not responding"
	@echo ""
	@echo "FastAPI:"
	@curl -s http://localhost:8000/health && echo "" && echo "  ✓ Running" || echo "  ✗ Not responding"
	@echo ""

# ====================================
# Individual Services
# ====================================

postgres:
	@echo "🗄️  Starting PostgreSQL..."
	pg_ctl -D ${HOME}/Library/PostgreSQL/15/data start

redis:
	@echo "⚡ Starting Redis..."
	redis-server --daemonize yes

mcp:
	@echo "🔧 Starting MCP Server..."
	cd 4sgm && python -m fastmcp run mcp_server.server:mcp

api:
	@echo "🚀 Starting FastAPI..."
	cd 4sgm && python -m uvicorn backend.app:app --reload --port 8000

frontend:
	@echo "🎨 Starting React Frontend..."
	cd 4sgm/frontend && npm run dev

# ====================================
# Development Tools
# ====================================

test:
	@echo "🧪 Running tests..."
	cd 4sgm && python -m pytest -v

lint:
	@echo "🔍 Linting code..."
	cd 4sgm && python -m ruff check .

format:
	@echo "✨ Formatting code..."
	cd 4sgm && python -m black . && python -m ruff check --fix .

database-init:
	@echo "📊 Initializing database..."
	cd 4sgm && python -c "from backend.database import init_db; init_db()"

# ====================================
# Docker Fallback
# ====================================

docker-start:
	@echo "🐳 Starting Docker Compose..."
	docker-compose up -d

docker-stop:
	@echo "🛑 Stopping Docker Compose..."
	docker-compose down

# ====================================
# Utility
# ====================================

.PHONY: setup clean start stop restart logs health \
        postgres redis mcp api frontend test lint format \
        database-init docker-start docker-stop help
```

### Step 6: Create Health Check Script

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/scripts/health-check.sh`

```bash
#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 4SGM Health Check"
echo "===================="
echo ""

# Check PostgreSQL
echo -n "PostgreSQL... "
if pg_isready -U user -d 4sgm &>/dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Check Redis
echo -n "Redis...      "
if redis-cli ping &>/dev/null | grep -q PONG; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Check FastAPI
echo -n "FastAPI...    "
if curl -s http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Check MCP (if available)
echo -n "MCP Server... "
if curl -s http://localhost:3000/health &>/dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${YELLOW}⚠ Not available${NC}"
fi

echo ""
```

### Step 7: Update .env.example

**Location**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/.env.example`

```bash
# Service Configuration
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/4sgm
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=4sgm
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Keys (obtain from respective services)
OPENAI_API_KEY=sk-YOUR_KEY_HERE
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=eyJhbGc...

# Service URLs
MCP_SERVER_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Logging
LOG_DIR=logs
LOG_LEVEL=INFO

# Development
DEBUG=false
RELOAD=true
```

---

## 3. Configuration Validation Checklist

### Pre-Implementation
- [ ] Python 3.10+ installed
- [ ] Homebrew installed
- [ ] Adequate disk space (>5GB)
- [ ] macOS 11+

### Installation Phase
- [ ] Brewfile dependencies installed
- [ ] PostgreSQL data directory created
- [ ] Redis configured
- [ ] Python virtual environment created
- [ ] Project dependencies installed

### Service Startup
- [ ] PostgreSQL starts and responds to health checks
- [ ] Redis starts and responds to PING
- [ ] MCP server loads 25+ tools
- [ ] FastAPI connects to MCP server
- [ ] Health endpoints return 200 OK

### Integration Testing
- [ ] Frontend connects to API
- [ ] Chat endpoint responds
- [ ] Streaming works (SSE)
- [ ] MCP tools are callable
- [ ] Database queries work
- [ ] Cache operations work

---

## 4. Manual Service Testing

### Test PostgreSQL
```bash
# Start PostgreSQL
pg_ctl -D ${HOME}/Library/PostgreSQL/15/data start

# Test connection
psql -U user -d 4sgm -c "SELECT 1"

# Check version
psql --version
```

### Test Redis
```bash
# Start Redis
redis-server --daemonize yes

# Test connection
redis-cli ping

# Test data
redis-cli SET test "Hello" && redis-cli GET test
```

### Test MCP Server
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm
python -m fastmcp run mcp_server.server:mcp
# Should show: "Serving MCP on stdio" or similar
```

### Test FastAPI
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm
python -m uvicorn backend.app:app --port 8000
# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

### Test Integration
```bash
# Health check
curl http://localhost:8000/health

# List tools
curl http://localhost:8000/tools

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello"}'
```

---

## 5. Troubleshooting Guide

### PostgreSQL Won't Start
```bash
# Check if already running
pg_isready

# Check logs
tail -20 ~/Library/PostgreSQL/15/data/postgresql.log

# Try to start with more info
pg_ctl -D ~/Library/PostgreSQL/15/data start -l pglog.txt

# Reset if corrupted
pg_ctl -D ~/Library/PostgreSQL/15/data stop
rm -rf ~/Library/PostgreSQL/15/data/*
initdb -D ~/Library/PostgreSQL/15/data
```

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Find what's using port 5432
lsof -i :5432

# Kill process (use PID from above)
kill -9 <PID>
```

### Python Import Errors
```bash
# Reset virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### MCP Server Won't Start
```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Try manual startup
cd 4sgm
PYTHONPATH=/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm \
  python -m fastmcp run mcp_server.server:mcp

# Check tool definitions
python -c "from mcp_server.server import mcp; print(dir(mcp))"
```

---

## 6. Performance Optimization Tips

### Reduce Memory Usage
- Disable unused tools in MCP server
- Use connection pooling for database
- Enable Redis compression

### Improve Startup Time
- Pre-warm Python bytecode
- Use hypercorn instead of uvicorn
- Parallelize service startup

### Network Optimization
- Use Unix sockets for local connections
- Enable HTTP/2 in Caddy
- Reduce verbose logging

---

## 7. Deliverables Checklist

- [ ] `Brewfile` - Dependency declaration
- [ ] `process-compose.yaml` - Process orchestration
- [ ] `Caddyfile` - Reverse proxy configuration
- [ ] `Makefile` - Development commands
- [ ] `scripts/setup-local-dev.sh` - Setup automation
- [ ] `scripts/health-check.sh` - Health monitoring
- [ ] Updated `.env.example` - Configuration template
- [ ] Documentation - Local development guide
- [ ] Test suite passing
- [ ] Performance benchmarks

---

## 8. Timeline & Milestones

| Milestone | Timeline | Status |
|-----------|----------|--------|
| Environment setup | Day 1 AM | Pending |
| Brewfile creation | Day 1 AM | Pending |
| process-compose configuration | Day 1 PM | Pending |
| Initial testing | Day 1 PM | Pending |
| Caddyfile & reverse proxy | Day 2 AM | Pending |
| Makefile & scripts | Day 2 AM | Pending |
| Full integration testing | Day 2 PM | Pending |
| Performance benchmarking | Day 3 | Pending |
| Documentation finalization | Day 3 | Pending |

---

## 9. Success Metrics

- All 5 services start in <15 seconds
- <450MB total memory usage
- <1ms latency between services
- 100% health check pass rate
- 0 startup failures in 10 consecutive runs
- Full test suite passing
- Documentation complete and accurate

---

**Document Version**: 1.0
**Status**: Ready for Implementation
**Last Updated**: January 31, 2026
