#!/usr/bin/env bash
set -euo pipefail

# 4SGM Health Check Script
# Monitors the health of all services

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CHECK_INTERVAL=${1:-5}  # Default 5 seconds
VERBOSE=${2:-false}

print_header() {
    echo -e "${BLUE}"
    echo "================================"
    echo "  4SGM Health Check"
    echo "================================"
    echo -e "${NC}"
}

print_status() {
    local service=$1
    local status=$2
    local message=$3

    if [ "$status" = "ok" ]; then
        printf "  %-20s ${GREEN}✓ %s${NC}\n" "$service" "$message"
    elif [ "$status" = "warn" ]; then
        printf "  %-20s ${YELLOW}⚠ %s${NC}\n" "$service" "$message"
    else
        printf "  %-20s ${RED}✗ %s${NC}\n" "$service" "$message"
    fi
}

check_postgres() {
    if pg_isready -U user -d 4sgm > /dev/null 2>&1; then
        print_status "PostgreSQL" "ok" "Running (port 5432)"
        return 0
    else
        print_status "PostgreSQL" "error" "Not responding"
        return 1
    fi
}

check_redis() {
    if redis-cli ping > /dev/null 2>&1; then
        local memory=$(redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        print_status "Redis" "ok" "Running (port 6379) - $memory"
        return 0
    else
        print_status "Redis" "error" "Not responding"
        return 1
    fi
}

check_fastapi() {
    local response=$(curl -s -w "%{http_code}" -o /tmp/health.json http://localhost:8000/health)

    if [ "$response" = "200" ]; then
        local status=$(jq -r '.status' /tmp/health.json 2>/dev/null)
        local mcp=$(jq -r '.mcp_connected' /tmp/health.json 2>/dev/null)

        if [ "$mcp" = "true" ]; then
            print_status "FastAPI" "ok" "Running (port 8000) - MCP connected"
        else
            print_status "FastAPI" "warn" "Running (port 8000) - MCP not connected"
        fi
        return 0
    else
        print_status "FastAPI" "error" "Not responding"
        return 1
    fi
}

check_mcp() {
    if pgrep -f "fastmcp run" > /dev/null 2>&1; then
        print_status "MCP Server" "ok" "Running (stdio)"
        return 0
    else
        print_status "MCP Server" "warn" "Not running"
        return 1
    fi
}

check_frontend() {
    local response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:3001)

    if [ "$response" = "200" ] || [ "$response" = "404" ]; then
        print_status "Frontend" "ok" "Running (port 3001)"
        return 0
    else
        print_status "Frontend" "warn" "Not responding"
        return 1
    fi
}

get_process_stats() {
    echo ""
    echo "📊 Process Statistics:"
    echo ""

    # PostgreSQL
    if pgrep -f "postgres" > /dev/null; then
        local pid=$(pgrep -f "postgres" | head -1)
        local mem=$(ps -p $pid -o rss= | awk '{printf "%.0f MB", $1/1024}')
        printf "  %-20s %s\n" "PostgreSQL PID" "$pid ($mem)"
    fi

    # Redis
    if pgrep -f "redis-server" > /dev/null; then
        local pid=$(pgrep -f "redis-server" | head -1)
        local mem=$(ps -p $pid -o rss= | awk '{printf "%.0f MB", $1/1024}')
        printf "  %-20s %s\n" "Redis PID" "$pid ($mem)"
    fi

    # Python (FastAPI/MCP)
    if pgrep -f "uvicorn" > /dev/null; then
        local pid=$(pgrep -f "uvicorn" | head -1)
        local mem=$(ps -p $pid -o rss= | awk '{printf "%.0f MB", $1/1024}')
        printf "  %-20s %s\n" "FastAPI PID" "$pid ($mem)"
    fi

    if pgrep -f "fastmcp" > /dev/null; then
        local pid=$(pgrep -f "fastmcp" | head -1)
        local mem=$(ps -p $pid -o rss= | awk '{printf "%.0f MB", $1/1024}')
        printf "  %-20s %s\n" "MCP Server PID" "$pid ($mem)"
    fi

    # Frontend
    if pgrep -f "node" > /dev/null; then
        local pid=$(pgrep -f "node" | head -1)
        local mem=$(ps -p $pid -o rss= | awk '{printf "%.0f MB", $1/1024}')
        printf "  %-20s %s\n" "Frontend PID" "$pid ($mem)"
    fi
}

run_checks() {
    print_header
    echo "Services:"
    echo ""

    local passed=0
    local failed=0
    local warned=0

    if check_postgres; then ((passed++)); else ((failed++)); fi
    if check_redis; then ((passed++)); else ((failed++)); fi
    if check_mcp; then ((warned++)); else ((failed++)); fi
    if check_fastapi; then ((passed++)); else ((failed++)); fi
    if check_frontend; then ((warned++)); else ((failed++)); fi

    get_process_stats

    echo ""
    echo "Summary:"
    printf "  %-20s %d\n" "Passed" "$passed"
    printf "  %-20s %d\n" "Warnings" "$warned"
    printf "  %-20s %d\n" "Failed" "$failed"
    echo ""

    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✅ All critical services OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Some services failed${NC}"
        return 1
    fi
}

if [ "$CHECK_INTERVAL" = "-watch" ] || [ "$CHECK_INTERVAL" = "-w" ]; then
    # Continuous monitoring mode
    WATCH_INTERVAL=${VERBOSE:-5}
    echo "Watching health status every ${WATCH_INTERVAL}s (press Ctrl+C to exit)..."
    echo ""

    while true; do
        clear
        run_checks
        sleep "$WATCH_INTERVAL"
    done
else
    # Single check
    run_checks
    exit $?
fi
