# 4SGM Local Development Guide

**Quick Reference for Native Process Orchestration**

---

## Quick Start (5 Minutes)

### 1. Initial Setup
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm

# Install dependencies (one-time)
make setup
```

### 2. Start All Services
```bash
make start
# Or: process-compose up
```

### 3. Open API Docs
```bash
open http://localhost:8000/docs
```

### 4. Run Tests
```bash
make test
```

### 5. Stop Services
```bash
make stop
# Or: Ctrl+C in terminal
```

---

## Common Development Tasks

### View Service Logs
```bash
# All services
make logs

# Or tail specific log files
tail -f logs/fastapi.log
tail -f logs/mcp_server.log
tail -f logs/postgres.log
tail -f logs/redis.log

# With lnav (fancy log viewer)
make tail-logs
```

### Check Service Health
```bash
# Quick health check
make health

# Detailed health check
make check-health

# Watch health continuously
./scripts/health-check.sh -watch
```

### Run Individual Services
```bash
# MCP Server (stdio)
make mcp

# FastAPI (port 8000)
make api

# React Frontend (port 3001)
make frontend

# PostgreSQL
make postgres

# Redis
make redis
```

### Testing & Quality
```bash
# Run all tests
make test

# Quick test run (non-slow tests only)
make test-quick

# Test with coverage report
make test-coverage

# Lint code
make lint

# Format code
make format

# Type checking
make type-check

# Watch tests (auto-run on changes)
make watch
```

### Database Operations
```bash
# Initialize database
make database-init

# Reset database
make db-reset

# Seed with test data
make db-seed

# Run migrations
make db-migrate
```

### Documentation
```bash
# Open Swagger UI
make docs

# Open ReDoc
make docs-redoc
```

---

## Environment Configuration

### Update .env File
```bash
# Copy template if it doesn't exist
cp .env.example .env

# Edit with your secrets
nano .env
```

### Required Environment Variables
```bash
# API Keys
OPENAI_API_KEY=sk-YOUR_KEY
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=eyJhbGc...

# Database (usually pre-configured)
DATABASE_URL=postgresql://user:password@localhost:5432/4sgm

# Redis (usually pre-configured)
REDIS_URL=redis://localhost:6379/0
```

---

## Service Ports & Endpoints

| Service | Port | Health Check | Purpose |
|---------|------|--------------|---------|
| PostgreSQL | 5432 | `pg_isready` | Database |
| Redis | 6379 | `redis-cli ping` | Cache |
| MCP Server | stdio | Process check | Tool execution |
| FastAPI | 8000 | `/health` | Main API |
| Frontend | 3001 | HTTP check | React dev server |
| Caddy (optional) | 9000 | HTTP check | Reverse proxy |

### API Endpoints (Port 8000)
```
GET    /health              Health check
GET    /docs                Swagger UI
GET    /redoc               ReDoc documentation
GET    /openapi.json        OpenAPI schema
GET    /tools               List MCP tools
POST   /chat                Chat (request/response)
POST   /chat/stream         Chat (streaming)
```

---

## Troubleshooting

### Service Won't Start

**PostgreSQL won't start**:
```bash
# Check if already running
pg_isready

# Kill existing process
pkill -f "postgres"

# Try starting again
pg_ctl -D ~/Library/PostgreSQL/15/data start

# Check logs
tail -20 ~/Library/PostgreSQL/15/data/postgresql.log
```

**Redis won't start**:
```bash
# Check if already running
redis-cli ping

# Kill existing process
pkill -f "redis-server"

# Start again
redis-server
```

**FastAPI won't start**:
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process (replace PID)
kill -9 <PID>

# Check Python dependencies
python -c "import fastapi; print('OK')"

# Reinstall dependencies
make clean
make setup
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Kill the process
kill -9 <PID>
```

### Import Errors
```bash
# Reset Python environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### MCP Server Issues
```bash
# Test MCP server directly
cd 4sgm
python -m fastmcp run mcp_server.server:mcp

# Check PYTHONPATH
echo $PYTHONPATH

# Verify tools load
python -c "from mcp_server.server import mcp; print('MCP loaded')"
```

### Database Connection Issues
```bash
# Test connection directly
psql -U user -d 4sgm -c "SELECT 1"

# Check credentials in .env
grep DATABASE_URL .env

# Ensure PostgreSQL is running
make postgres

# Reset database if corrupted
make db-reset
```

---

## Performance Tips

### Reduce Memory Usage
```bash
# Disable unused MCP tools
# Edit 4sgm/mcp_server/server.py

# Use connection pooling
# Already configured in backend/app.py
```

### Improve Startup Time
```bash
# Parallel startup is automatic with process-compose
# Typical startup: 10-15 seconds

# Warmup Python bytecode
python -m compileall 4sgm/
```

### Development Workflow
```bash
# Terminal 1: Start services
make start

# Terminal 2: Watch tests
make watch

# Terminal 3: View logs
make logs

# Terminal 4: Develop
# Use IDE with hot-reload enabled
```

---

## Useful Commands Quick Reference

```bash
# Display help
make help
make -n <target>        # Dry-run (show what would execute)

# Service control
make start              # Start all services
make stop               # Stop gracefully
make restart            # Restart all
make health             # Check health

# View logs
make logs               # Tail all logs
tail -f logs/*.log      # Follow specific logs
make tail-logs          # Use lnav for navigation

# Testing
make test               # Full test suite
make test-quick         # Quick tests only
make test-coverage      # With coverage report
make lint               # Run linter
make format             # Auto-format code

# Database
make database-init      # Initialize
make db-reset           # Reset to clean state
make db-seed            # Load test data

# Cleanup
make clean              # Remove artifacts
make deep-clean         # Remove venv, caches, etc.
make prune              # Remove old logs

# Docker fallback
make docker-start       # Use Docker Compose instead
make docker-stop        # Stop Docker services
```

---

## Development Workflow

### Typical Session
```bash
# 1. Setup (first time)
make setup

# 2. Start services
make start

# 3. In another terminal, watch tests
make watch

# 4. Make code changes and save
# Tests auto-run, live reload active

# 5. View logs if needed
make logs

# 6. Check health
make health

# 7. Stop when done
make stop
```

### Contributing Code
```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit files in your IDE

# 3. Format and lint
make format
make lint

# 4. Run tests
make test

# 5. Commit changes
git add .
git commit -m "feat: description"

# 6. Push
git push origin feature/my-feature
```

---

## IDE Integration

### VS Code
```json
{
  "launch": {
    "version": "0.2.0",
    "configurations": [
      {
        "name": "FastAPI Debug",
        "type": "python",
        "request": "launch",
        "module": "uvicorn",
        "args": ["backend.app:app", "--reload"],
        "cwd": "${workspaceFolder}/4sgm"
      }
    ]
  }
}
```

### PyCharm
1. Set Python interpreter to `.venv/bin/python`
2. Set working directory to `4sgm/`
3. Create run configuration for `uvicorn backend.app:app --reload`

---

## Advanced Topics

### Enable Verbose Logging
```bash
# Set LOG_LEVEL in .env
LOG_LEVEL=DEBUG

# Or override per service
LOG_LEVEL=DEBUG make api
```

### Remote Debugging
```bash
# Add to FastAPI startup
import pdb; pdb.set_trace()

# Or use debugpy for VS Code
pip install debugpy
# Configure VS Code to connect
```

### Performance Profiling
```bash
# Time service startup
make profile

# Profile specific function
python -m cProfile -s cumulative 4sgm/backend/app.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler 4sgm/backend/app.py
```

### Database Backup & Restore
```bash
# Backup
pg_dump -U user 4sgm > backup.sql

# Restore
psql -U user 4sgm < backup.sql
```

### Load Testing
```bash
# Install load testing tool
pip install locust

# Create locustfile.py
# Run: locust -f locustfile.py -u 100 -r 10 --run-time 1m
```

---

## Useful Links

- FastAPI Documentation: https://fastapi.tiangolo.com/
- LangGraph: https://langchain-ai.github.io/langgraph/
- MCP Protocol: https://modelcontextprotocol.io/
- PostgreSQL: https://www.postgresql.org/docs/15/
- Redis: https://redis.io/documentation/
- process-compose: https://github.com/F1bonacc1/process-compose
- Caddy: https://caddyserver.com/docs/

---

## Getting Help

1. Check logs: `make logs`
2. Health check: `make health`
3. Run tests: `make test`
4. Check documentation: `make docs`
5. Review code comments and docstrings
6. Ask team members or check project README

---

**Last Updated**: January 31, 2026
**Status**: Production Ready
