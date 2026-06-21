# 4SGM Native Process Orchestration - Design Document

**Date**: January 31, 2026
**Project**: 4SGM (LangGraph + MCP Server)
**Scope**: 5 Core Services + 1 Reverse Proxy
**Status**: Design Phase

---

## 1. Executive Summary

This document outlines the design for native process orchestration of the 4SGM AI/MCP system using `process-compose` and native OS process management. The current Docker Compose setup (5 containers) will be decomposed into coordinated native processes running on the host system with sophisticated dependency management, health monitoring, and graceful lifecycle handling.

**Key Benefits**:
- Simplified local development without Docker overhead
- Reduced memory/CPU footprint vs containers
- Better IDE integration and debugging
- Native process monitoring and restart policies
- Faster startup and iteration cycles
- Easier resource profiling

---

## 2. Current State Analysis

### 2.1 Docker Compose Architecture

Current services:
1. **MCP Server** (port 3000)
   - 25+ e-commerce tools
   - FastMCP framework
   - Health check: `curl http://localhost:3000/health`
   - Dependencies: None (startup service)

2. **FastAPI Backend** (port 8000)
   - LangGraph agent orchestration
   - MCP client (LangChain adapters)
   - Health check: `curl http://localhost:8000/health`
   - Dependencies: MCP Server, PostgreSQL
   - Startup: `python cli.py api`

3. **PostgreSQL** (port 5432)
   - User credential: `user:password`
   - Database: `4sgm`
   - Health check: `pg_isready -U user`
   - No dependencies

4. **Redis** (port 6379)
   - Caching layer
   - Health check: `redis-cli ping`
   - No dependencies

5. **React Frontend** (Vercel AI SDK)
   - Development: `npm run dev`
   - Not containerized in current setup
   - Depends on: FastAPI backend

### 2.2 Communication Patterns

```
React Frontend (Browser)
    ↓ HTTP/SSE
FastAPI Backend (8000)
    ↓ stdio (MCP protocol)
MCP Server (3000)
    ↓ Tool execution
PostgreSQL (5432) + Redis (6379)
```

### 2.3 Current Pain Points

1. Docker overhead on local development
2. Slow container rebuild cycles
3. Limited IDE debugging integration
4. Complex volume mounting
5. Network latency between containers

---

## 3. Native Orchestration Architecture

### 3.1 Process Composition Strategy

Using `process-compose` (YAML-based process orchestrator):

```
Process Orchestration Layer
├─ Startup Supervisor
├─ Health Monitor
├─ Lifecycle Manager
├─ Log Aggregation
└─ Graceful Shutdown Handler

Core Processes
├─ MCP Server (stdio transport)
├─ FastAPI Backend (HTTP transport)
├─ PostgreSQL (TCP/Unix socket)
└─ Redis (TCP)

Support Services
├─ Log collector
├─ Health checker
└─ Environment manager
```

### 3.2 Service Dependency Graph

```
┌─────────────────────────────────────┐
│    PostgreSQL (Port 5432)           │
│    - Eager startup                  │
│    - Health: pg_isready             │
│    - No dependencies                │
└────────────────┬────────────────────┘
                 │
                 ├─→ ┌──────────────────────────────────┐
                 │   │  Redis (Port 6379)               │
                 │   │  - Eager startup                 │
                 │   │  - Health: redis-cli ping        │
                 │   │  - No dependencies               │
                 │   └──────────┬───────────────────────┘
                 │              │
                 └──────────────┤
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐         ┌─────────────────┐
        │   MCP Server    │         │ FastAPI Backend │
        │  (Stdio Port)   │◄────────│  (HTTP 8000)    │
        │  - Tool Exec    │  MCP    │  - Agent Orch   │
        │  - 25+ Tools    │  Calls  │  - Tool Loader  │
        │                 │         │                 │
        │ Health:         │         │ Health:         │
        │  /health        │         │  /health        │
        │  (Liveness)     │         │  (Readiness)    │
        └─────────────────┘         └─────────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │React Frontend│
                                    │ (Browser Dev)│
                                    └──────────────┘
```

### 3.3 Process Startup Order (Sequential)

1. **Phase 1** (Parallel startup):
   - PostgreSQL (5s startup time)
   - Redis (1s startup time)

2. **Phase 2** (Parallel startup):
   - MCP Server (depends on nothing)
   - Wait for health: curl checks

3. **Phase 3** (Requires all above):
   - FastAPI Backend
   - Wait for /health endpoint

4. **Phase 4** (Manual):
   - React Frontend (development server)
   - Connects to http://localhost:8000

### 3.4 Health Monitoring Strategy

**Startup Health Checks**:
- PostgreSQL: `pg_isready -U user`
- Redis: `redis-cli ping`
- MCP Server: `curl http://localhost:3000/health` (if HTTP endpoint exists)
- FastAPI: `curl http://localhost:8000/health`

**Liveness Probes**:
- Periodic health checks every 30 seconds
- Restart policy: `unless-stopped` for critical services
- Log monitoring for error patterns

**Readiness Indicators**:
- FastAPI must wait for MCP server ready
- MCP server startup should be near-instant
- Database connection pooling ready

---

## 4. Environment & Configuration Management

### 4.1 Environment Variables

**Global** (`.env`):
```bash
# Service Configuration
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/4sgm
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=4sgm

# Secrets (source from external store)
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_KEY=${SUPABASE_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}

# Service URLs (for service-to-service communication)
MCP_SERVER_URL=http://localhost:3000/mcp
REDIS_URL=redis://localhost:6379

# Port Configuration
MCP_PORT=3000
API_PORT=8000
POSTGRES_PORT=5432
REDIS_PORT=6379

# Logging
LOG_DIR=./logs
```

### 4.2 Process Environment Files

Each service gets:
1. Inherited global `.env`
2. Service-specific overrides
3. Runtime variables (PIDs, ports)

---

## 5. Process Compose Configuration

### 5.1 process-compose.yaml Structure

```yaml
version: "3.0"

environment:
  - LOG_DIR=logs
  - PYTHON_PATH=/Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm

processes:
  postgres:
    command: postgres service launcher
    working_dir: .
    env:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=4sgm
    depends_on:
      - none
    startup:
      type: notify
      action: wait
    restart_policy:
      backoff: exponential
      max_restarts: 5
      wait_period: 1s
    health:
      exec:
        command: pg_isready -U user
      initial_delay: 1s
      period: 10s

  redis:
    command: redis-server service launcher
    depends_on:
      - postgres: running_ok
    startup:
      type: notify
      action: wait
    health:
      exec:
        command: redis-cli ping

  mcp_server:
    command: python -m fastmcp run mcp_server.server:mcp
    working_dir: /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm
    env_file: .env
    depends_on:
      - postgres: running_ok
      - redis: running_ok
    startup:
      type: notify
      action: wait
    restart_policy:
      backoff: exponential
      max_restarts: 5

  fastapi:
    command: python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
    working_dir: /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm
    env_file: .env
    depends_on:
      - mcp_server: running_ok
      - postgres: running_ok
    startup:
      type: notify
      action: wait
    health:
      exec:
        command: curl -f http://localhost:8000/health

  frontend:
    command: npm run dev
    working_dir: /Users/kooshapari/temp-PRODVERCEL/485/kush/4sgm/4sgm/frontend
    depends_on:
      - fastapi: running_ok
    startup:
      type: notify
      action: wait
```

---

## 6. Service-Specific Orchestration Details

### 6.1 PostgreSQL Native Process

**Approach**: Use system PostgreSQL or local binary

```bash
# Check if PostgreSQL is installed
which psql

# If not installed via Homebrew:
brew install postgresql@15

# Initialize data directory (first time)
initdb -D /usr/local/var/postgres

# Start PostgreSQL
pg_ctl -D /usr/local/var/postgres start

# Health check
pg_isready -U user -d 4sgm
```

**Process Compose Entry**:
- Check for existing PostgreSQL server
- Use socket connection if available
- Fall back to TCP connection

**Container Fallback**:
- If native PostgreSQL unavailable, use `docker run postgres:15-alpine`

### 6.2 Redis Native Process

**Approach**: Use system Redis

```bash
# Install via Homebrew
brew install redis

# Start redis-server
redis-server /usr/local/etc/redis.conf

# Health check
redis-cli ping
```

### 6.3 MCP Server Process

**Command**: `python -m fastmcp run mcp_server.server:mcp`

**Environment**:
- `PYTHONPATH` set to project root
- `LOG_LEVEL=INFO`
- Inherit from `.env`

**Stdio Communication**:
- No HTTP port exposure (internal)
- Communicates via stdin/stdout with FastAPI
- This prevents port conflicts during development

**Health**:
- Check tool loading capability
- Log file monitoring for startup errors

### 6.4 FastAPI Backend Process

**Command**: `python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload`

**Features**:
- Auto-reload on file changes (development)
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Depends On**:
- PostgreSQL running (connection pool)
- Redis available (caching)
- MCP Server ready (tool loading)

**Health Endpoint**: `GET /health`
- Returns: `{"status": "ok", "mcp_connected": true}`

### 6.5 React Frontend Process

**Command**: `npm run dev` (Next.js development server)

**Configuration**:
- Works with Vercel AI SDK v6
- Connects to `http://localhost:8000` (FastAPI backend)
- Port: 3001 or 3002 (auto-increment)

**Not Managed by Process Compose**:
- Optional manual startup
- Can be started in separate terminal
- IDE integration preferred

---

## 7. Reverse Proxy Configuration (Caddy)

### 7.1 Caddyfile Design

```caddyfile
# Development routing
localhost:9000 {
    # API routing
    handle /api/* {
        uri strip_prefix /api
        reverse_proxy localhost:8000
    }

    # MCP server access (internal only)
    handle /mcp/* {
        uri strip_prefix /mcp
        reverse_proxy localhost:3000
    }

    # Database admin (pgAdmin)
    handle /pgadmin/* {
        uri strip_prefix /pgadmin
        reverse_proxy localhost:5050
    }

    # Redis commander
    handle /redis/* {
        uri strip_prefix /redis
        reverse_proxy localhost:8081
    }

    # Frontend fallback
    handle {
        reverse_proxy localhost:3001 localhost:3002
    }
}

# Production-like configuration
localhost:9001 {
    # Single origin API
    reverse_proxy localhost:8000
}
```

### 7.2 Caddy Installation & Setup

```bash
# Install Caddy via Homebrew
brew install caddy

# Start Caddy with custom config
caddy run --config Caddyfile

# Or use systemd/launchd service
brew services start caddy
```

---

## 8. Development Tools Integration

### 8.1 Brewfile (Dependency Management)

Declares all native dependencies:

```ruby
tap "hashicorp/tap"

# Database
brew "postgresql@15"
brew "redis"

# Web Server
brew "caddy"

# Python
brew "python@3.10"
brew "uv"

# Development
brew "just"
brew "watchman"
brew "direnv"

# Monitoring
brew "btop"
brew "lnav"

# Optional: UI Tools
cask "pgadmin4"
cask "redis-pro"
```

### 8.2 Makefile Commands

```makefile
# System setup
setup:
  brew install -r Brewfile

# Service management
start:
  process-compose up

stop:
  process-compose down

logs:
  process-compose logs -f

# Individual service control
postgres-start:
  pg_ctl -D /usr/local/var/postgres start

redis-start:
  redis-server /usr/local/etc/redis.conf

# Cleanup
clean:
  rm -rf logs/
  find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 9. File Structure

```
4sgm/
├── .env                          # Shared environment
├── .env.example                  # Template
├── Brewfile                      # Brew dependencies
├── Caddyfile                     # Reverse proxy config
├── Makefile                      # Development commands
├── process-compose.yaml          # Process orchestration
├── docker-compose.yml            # Fallback (keep for CI/CD)
│
├── scripts/
│   ├── setup-local-dev.sh       # Local setup script
│   ├── health-check.sh          # Health monitoring
│   ├── start-services.sh        # Start all services
│   └── docker-fallback.sh       # Docker fallback
│
├── docs/
│   └── plans/
│       ├── 4sgm-native-orchestration-design.md     # This file
│       ├── 4sgm-native-orchestration-implementation.md
│       └── local-development-guide.md
│
├── 4sgm/
│   ├── backend/                 # FastAPI app
│   ├── mcp_server/             # MCP server
│   ├── frontend/               # React app
│   └── cli.py                  # CLI entry
│
└── .github/
    └── workflows/
        └── docker-ci.yml       # CI/CD (Docker fallback)
```

---

## 10. Failure Modes & Recovery

### 10.1 PostgreSQL Down

**Detection**: `pg_isready` fails
**Impact**: FastAPI cannot connect
**Recovery**:
1. `pg_ctl -D /usr/local/var/postgres restart`
2. FastAPI automatically retries connection
3. If persistent: `brew reinstall postgresql@15`

### 10.2 MCP Server Down

**Detection**: Health check fails
**Impact**: Agent cannot call tools
**Recovery**:
1. Check logs: `logs/mcp_server.log`
2. Restart: `process-compose restart mcp_server`
3. Manual restart: `python -m fastmcp run mcp_server.server:mcp`

### 10.3 FastAPI Down

**Detection**: Health check fails
**Impact**: Frontend cannot communicate
**Recovery**:
1. Check database connection
2. Check MCP server availability
3. Restart: `process-compose restart fastapi`

### 10.4 Redis Down

**Detection**: Redis client connection fails
**Impact**: Caching disabled (non-critical)
**Recovery**:
1. Restart: `redis-server`
2. Clear cache if corrupted: `redis-cli FLUSHALL`

---

## 11. Monitoring & Logging

### 11.1 Log Directory Structure

```
logs/
├── postgres.log         # PostgreSQL startup/errors
├── redis.log           # Redis startup/errors
├── mcp_server.log      # MCP server output
├── fastapi.log         # FastAPI server output
└── orchestrator.log    # process-compose logs
```

### 11.2 Log Aggregation

Option 1: Use `process-compose` built-in logging
Option 2: Use `lnav` for log navigation:

```bash
lnav logs/*.log
```

Option 3: Use `tail` for real-time monitoring:

```bash
tail -f logs/*.log
```

---

## 12. Performance Characteristics

### 12.1 Startup Time (Expected)

- PostgreSQL: 3-5 seconds (initialization)
- Redis: 1-2 seconds
- MCP Server: 2-3 seconds (tool loading)
- FastAPI: 2-3 seconds (agent setup)
- **Total**: ~10-15 seconds (parallel)

### 12.2 Resource Usage (vs Docker)

| Component | Docker | Native | Delta |
|-----------|--------|--------|-------|
| PostgreSQL | 100MB | 80MB | -20% |
| Redis | 50MB | 30MB | -40% |
| MCP Server | 200MB | 120MB | -40% |
| FastAPI | 300MB | 180MB | -40% |
| **Total** | **650MB** | **410MB** | **-37%** |

### 12.3 Network Latency

| Path | Docker | Native | Delta |
|------|--------|--------|-------|
| FastAPI→MCP | 5-10ms | <1ms | -95% |
| FastAPI→DB | 2-5ms | <1ms | -95% |
| Frontend→API | 10-20ms | 5-10ms | -50% |

---

## 13. CI/CD Considerations

### 13.1 Local Development

- Use native process orchestration (`process-compose`)
- Fast iteration, IDE integration
- Closer to production behavior

### 13.2 CI/CD Pipeline

- Keep Docker Compose for containerized testing
- Use same docker-compose.yml as fallback
- GitHub Actions can use native services or containers

### 13.3 Production Deployment

- Use Kubernetes (if scaling)
- Or: Supervisor + systemd on dedicated servers
- Or: Use process-compose on containerized VMs

---

## 14. Alternative Implementations

### 14.1 Supervisor (Heavy-weight)

```ini
[program:mcp_server]
command=/usr/bin/python -m fastmcp run mcp_server.server:mcp
autostart=true
autorestart=true
stderr_logfile=/var/log/mcp_server.err.log
stdout_logfile=/var/log/mcp_server.out.log
```

### 14.2 Systemd (Complex)

```ini
[Unit]
Description=4SGM MCP Server
After=network.target

[Service]
Type=simple
User=developer
WorkingDirectory=/path/to/4sgm
ExecStart=/usr/bin/python -m fastmcp run mcp_server.server:mcp
Restart=on-failure
```

### 14.3 Docker (Current Fallback)

Keep existing `docker-compose.yml` for:
- CI/CD pipelines
- Teams without local PostgreSQL/Redis
- Production-like environments

---

## 15. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| PostgreSQL not installed | Medium | High | Brew install, Docker fallback |
| Port conflicts (3000, 8000, 5432) | Low | Medium | Check with `lsof`, adjust ports |
| Environment variable mismatch | Medium | Medium | `.env` template, validation script |
| Process zombie (hung process) | Low | Medium | Process Compose cleanup, systemd |
| Development/production parity | Low | Low | Document differences, test both |

---

## 16. Success Criteria

✓ All 5 services start via `process-compose up`
✓ Health checks pass within 15 seconds
✓ FastAPI can load MCP tools
✓ Agent can execute tool calls
✓ React frontend connects and works
✓ Graceful shutdown with `Ctrl+C`
✓ Logs are centralized in `logs/` directory
✓ <50% resource usage vs Docker
✓ <10ms latency between services

---

## 17. Next Steps

1. **Implementation Phase**:
   - Create `process-compose.yaml`
   - Create `Brewfile`
   - Create `Caddyfile`
   - Create setup scripts

2. **Testing Phase**:
   - Local development workflow
   - Service restart scenarios
   - Log aggregation validation

3. **Documentation Phase**:
   - Local development guide
   - Troubleshooting guide
   - Performance benchmarking

---

## References

- [process-compose](https://github.com/F1bonacc1/process-compose)
- [Homebrew](https://brew.sh)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Caddy](https://caddyserver.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [MCP](https://modelcontextprotocol.io/)

---

**Document Version**: 1.0
**Last Updated**: January 31, 2026
**Status**: Ready for Implementation
