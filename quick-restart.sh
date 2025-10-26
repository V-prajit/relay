#!/bin/bash

# Quick Restart Script for Demo
# Kills all services and restarts them

echo "🛑 Stopping all services..."
lsof -ti:8000,3001,3002 | xargs kill -9 2>/dev/null || echo "No services running"

echo ""
echo "🚀 Starting services..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend
echo "  → Starting backend (port 8000)..."
cd backend
python run.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a second for backend to start
sleep 2

# Start ripgrep API
echo "  → Starting Ripgrep API (port 3001)..."
cd ripgrep-api
npm run dev > ../logs/ripgrep.log 2>&1 &
RIPGREP_PID=$!
cd ..

# Wait a second
sleep 2

# Start frontend
echo "  → Starting Frontend (port 3002)..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Dashboard: http://localhost:3002"
echo "🔧 Backend API: http://localhost:8000"
echo "🔍 Ripgrep API: http://localhost:3001"
echo ""
echo "📝 Logs:"
echo "  - backend: logs/backend.log"
echo "  - ripgrep: logs/ripgrep.log"
echo "  - frontend: logs/frontend.log"
echo ""
echo "Process IDs:"
echo "  - Backend: $BACKEND_PID"
echo "  - Ripgrep: $RIPGREP_PID"
echo "  - Frontend: $FRONTEND_PID"
echo ""
echo "🎬 Wait 10 seconds, then open http://localhost:3002"
