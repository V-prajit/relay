#!/bin/bash

# BugRewind - Start All Services Script
# Starts Backend (8000), Ripgrep API (3001), and Frontend Dashboard (3002)

echo "========================================"
echo "  BugRewind - Starting All Services"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Kill existing processes on our ports
echo -e "${YELLOW}Checking for existing processes...${NC}"
for port in 8000 3001 3002; do
    if check_port $port; then
        echo -e "${YELLOW}Port $port is in use. Killing process...${NC}"
        kill -9 $(lsof -ti:$port) 2>/dev/null || true
        sleep 1
    fi
done
echo ""

# Create log directory
mkdir -p logs

# Start Backend API (Port 8000)
echo -e "${BLUE}[1/3] Starting Backend API (Python/FastAPI)...${NC}"
cd backend
python run.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "      → Backend PID: $BACKEND_PID"
echo -e "      → Logs: logs/backend.log"
cd ..
sleep 3

# Check if backend started
if check_port 8000; then
    echo -e "${GREEN}      ✓ Backend API running on http://localhost:8000${NC}"
else
    echo -e "${YELLOW}      ⚠ Backend may still be starting...${NC}"
fi
echo ""

# Start Ripgrep API (Port 3001)
echo -e "${BLUE}[2/3] Starting Ripgrep API (Node.js/Express)...${NC}"
cd ripgrep-api
npm run dev > ../logs/ripgrep.log 2>&1 &
RIPGREP_PID=$!
echo -e "      → Ripgrep PID: $RIPGREP_PID"
echo -e "      → Logs: logs/ripgrep.log"
cd ..
sleep 3

# Check if ripgrep started
if check_port 3001; then
    echo -e "${GREEN}      ✓ Ripgrep API running on http://localhost:3001${NC}"
else
    echo -e "${YELLOW}      ⚠ Ripgrep may still be starting...${NC}"
fi
echo ""

# Start Frontend Dashboard (Port 3002)
echo -e "${BLUE}[3/4] Starting Frontend Dashboard (Next.js)...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "      → Frontend PID: $FRONTEND_PID"
echo -e "      → Logs: logs/frontend.log"
cd ..
sleep 5

# Check if frontend started
if check_port 3002; then
    echo -e "${GREEN}      ✓ Frontend running on http://localhost:3002${NC}"
else
    echo -e "${YELLOW}      ⚠ Frontend may still be starting...${NC}"
fi
echo ""

# Start Slack Listener (Socket Mode)
echo -e "${BLUE}[4/4] Starting Slack Listener (Socket Mode)...${NC}"
cd slack-listener
npm start > ../logs/slack-listener.log 2>&1 &
SLACK_PID=$!
echo -e "      → Slack Listener PID: $SLACK_PID"
echo -e "      → Logs: logs/slack-listener.log"
cd ..
sleep 3

echo -e "${GREEN}      ✓ Slack Listener running (Socket Mode)${NC}"
echo ""

# Save PIDs to file for cleanup
echo "$BACKEND_PID" > .pids
echo "$RIPGREP_PID" >> .pids
echo "$FRONTEND_PID" >> .pids
echo "$SLACK_PID" >> .pids

echo "========================================"
echo -e "${GREEN}  All services started!${NC}"
echo "========================================"
echo ""
echo "📊 Service URLs:"
echo "   • Backend API:    http://localhost:8000"
echo "   • API Docs:       http://localhost:8000/docs"
echo "   • Ripgrep API:    http://localhost:3001"
echo "   • Dashboard:      http://localhost:3002"
echo "   • Slack Listener: Socket Mode (no URL, listening for /relay)"
echo ""
echo "📝 Logs available in:"
echo "   • Backend:  logs/backend.log"
echo "   • Ripgrep:  logs/ripgrep.log"
echo "   • Frontend: logs/frontend.log"
echo "   • Slack:    logs/slack-listener.log"
echo ""
echo "🛑 To stop all services, run: ./stop-all.sh"
echo ""
echo "⌛ Waiting for all services to initialize..."
echo "   Open http://localhost:3002 in your browser!"
echo ""

# Wait and show status
sleep 5
echo "Current status:"
curl -s http://localhost:8000/health 2>/dev/null && echo "" || echo "Backend: Starting..."
curl -s http://localhost:3001/api/health 2>/dev/null && echo "" || echo "Ripgrep: Starting..."
echo ""
echo "Press Ctrl+C to view logs (services will continue running)"
echo ""

# Tail logs (optional)
# Uncomment to show live logs:
# tail -f logs/*.log
