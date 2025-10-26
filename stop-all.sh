#!/bin/bash

# BugRewind - Stop All Services Script

echo "========================================"
echo "  BugRewind - Stopping All Services"
echo "========================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to kill process on port
kill_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}Stopping $name (port $port)...${NC}"
        kill -9 $(lsof -ti:$port) 2>/dev/null || true
        sleep 1
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            echo -e "${RED}  ✗ Failed to stop $name${NC}"
        else
            echo -e "${GREEN}  ✓ $name stopped${NC}"
        fi
    else
        echo -e "  • $name not running on port $port"
    fi
}

# Kill by saved PIDs first
if [ -f .pids ]; then
    echo "Stopping services by saved PIDs..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi
    done < .pids
    rm .pids
    sleep 2
fi

# Kill by port as fallback
kill_port 8000 "Backend API"
kill_port 3001 "Ripgrep API"
kill_port 3002 "Frontend Dashboard"

echo ""
echo -e "${GREEN}All services stopped!${NC}"
echo ""
