#!/bin/bash
# Test script for GitHub PR creation endpoint
# Usage: ./test_github_pr.sh [base_url]
# Example: ./test_github_pr.sh http://localhost:8000

BASE_URL="${1:-http://localhost:8000}"

echo "Testing GitHub PR Creation Endpoint"
echo "===================================="
echo "Base URL: $BASE_URL"
echo ""

# Test data - minimal required fields (NO patch_content)
REQUEST_DATA='{
  "repo_url": "https://github.com/V-prajit/relay",
  "branch_name": "test/github-pr-fix-verification",
  "title": "Test: Verify 404 fix for PR creation",
  "description": "## Summary\n\nThis is a test PR to verify that the 404 error fix works correctly.\n\n## Changes\n- Fixed router prefix configuration\n- Made patch_content optional\n\n## Testing\n- Manual test via curl\n- Postman Flow integration test"
}'

echo "1. Testing /api/github/create-pr endpoint..."
echo ""

# Make the request
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/github/create-pr" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_DATA")

# Extract HTTP status code (last line)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

# Extract response body (everything except last line)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
  echo "✅ SUCCESS! Endpoint is working"
  echo ""
  echo "Response:"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" -eq 404 ]; then
  echo "❌ ERROR 404: Endpoint not found"
  echo "   - Check if router prefix is correct"
  echo "   - Verify server is running"
  echo ""
  echo "Response:"
  echo "$BODY"
elif [ "$HTTP_CODE" -eq 422 ]; then
  echo "❌ ERROR 422: Validation error"
  echo "   - Check if patch_content is still required"
  echo "   - Verify request body matches model"
  echo ""
  echo "Response:"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
  echo "❌ ERROR $HTTP_CODE"
  echo ""
  echo "Response:"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
fi

echo ""
echo "===================================="

# Test health endpoint
echo "2. Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Test docs endpoint
echo "3. API Documentation available at:"
echo "   $BASE_URL/docs"
echo ""
