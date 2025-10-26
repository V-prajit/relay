#!/bin/bash

# Quick test script to verify dashboard setup

echo "========================================"
echo "  BugRewind Dashboard - Quick Test"
echo "========================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_endpoint() {
    local url=$1
    local name=$2

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 5)

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        return 1
    fi
}

# Check if services are running
check_running() {
    local port=$1
    local name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}✓${NC} $name is running on port $port"
        return 0
    else
        echo -e "${RED}✗${NC} $name is NOT running on port $port"
        return 1
    fi
}

echo "Step 1: Checking if services are running..."
echo ""
check_running 8000 "Backend API"
check_running 3001 "Ripgrep API"
check_running 3002 "Frontend Dashboard"
echo ""

echo "Step 2: Testing API endpoints..."
echo ""
test_endpoint "http://localhost:8000/health" "Backend health"
test_endpoint "http://localhost:8000/api/dashboard/health-summary" "Dashboard health summary"
test_endpoint "http://localhost:8000/api/dashboard/metrics" "Dashboard metrics"
test_endpoint "http://localhost:8000/api/dashboard/recent-prs" "Recent PRs"
test_endpoint "http://localhost:3001/api/health" "Ripgrep health"
echo ""

echo "Step 3: Sample API responses..."
echo ""
echo -e "${YELLOW}Health Summary:${NC}"
curl -s http://localhost:8000/api/dashboard/health-summary | python -m json.tool 2>/dev/null || echo "Could not fetch"
echo ""

echo -e "${YELLOW}Metrics:${NC}"
curl -s http://localhost:8000/api/dashboard/metrics | python -m json.tool 2>/dev/null || echo "Could not fetch"
echo ""

echo "========================================"
echo "  Test Complete!"
echo "========================================"
echo ""
echo "If all tests passed, open: http://localhost:3002"
echo ""
