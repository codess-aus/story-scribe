#!/bin/bash
# Integration test script for StoryScribe
# Tests all API endpoints and reports results

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
TEST_USER_ID="test_user_$(date +%s)"
PASSED=0
FAILED=0

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  StoryScribe Integration Test Suite   ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""
echo "Backend URL: $BACKEND_URL"
echo "Test User ID: $TEST_USER_ID"
echo ""

# Helper function to run a test
run_test() {
    local test_name="$1"
    local expected_status="$2"
    shift 2
    local curl_cmd=("$@")
    
    echo -n "Testing: $test_name ... "
    
    # Run curl and capture status code
    response=$(mktemp)
    status_code=$(curl -s -w "%{http_code}" -o "$response" "${curl_cmd[@]}")
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        
        # Show response if it's JSON (and not too long)
        if grep -q "application/json" <(curl -sI "${curl_cmd[@]}" | grep -i content-type) 2>/dev/null; then
            response_size=$(wc -c < "$response")
            if [ "$response_size" -lt 500 ]; then
                echo "  Response: $(cat "$response" | jq -c . 2>/dev/null || cat "$response")"
            fi
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "  Response: $(cat "$response")"
        FAILED=$((FAILED + 1))
    fi
    
    rm "$response"
    echo ""
}

# Test 1: Health Check
run_test "Health Check" "200" \
    "$BACKEND_URL/health"

# Test 2: Health Check Response Content
echo -n "Testing: Health Check Content ... "
health_response=$(curl -s "$BACKEND_URL/health")
if echo "$health_response" | jq -e '.status == "ok"' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Expected: {\"status\": \"ok\", ...}"
    echo "  Got: $health_response"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 3: Get Prompt (Memoir)
run_test "Get Writing Prompt (memoir)" "200" \
    "$BACKEND_URL/prompt?genre=memoir"

# Test 4: Get Prompt (Adventure)
run_test "Get Writing Prompt (adventure)" "200" \
    "$BACKEND_URL/prompt?genre=adventure"

# Test 5: Get Prompt (Reflection)
run_test "Get Writing Prompt (reflection)" "200" \
    "$BACKEND_URL/prompt?genre=reflection"

# Test 6: List Stories (Empty)
run_test "List Stories (should be empty)" "200" \
    -H "X-User-Id: $TEST_USER_ID" \
    "$BACKEND_URL/stories"

# Test 7: Create Story (Missing Header)
run_test "Create Story (missing user header)" "401" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"title":"Test","content":"Test content"}' \
    "$BACKEND_URL/stories"

# Test 8: Create Story (Success)
run_test "Create Story (success)" "200" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-User-Id: $TEST_USER_ID" \
    -d '{"title":"My First Memory","content":"I remember the first time I saw the ocean."}' \
    "$BACKEND_URL/stories"

# Test 9: Create Second Story
run_test "Create Second Story" "200" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-User-Id: $TEST_USER_ID" \
    -d '{"title":"A Lesson Learned","content":"My grandmother taught me about kindness."}' \
    "$BACKEND_URL/stories"

# Test 10: List Stories (Should have 2)
echo -n "Testing: List Stories (should have 2) ... "
response=$(curl -s -H "X-User-Id: $TEST_USER_ID" "$BACKEND_URL/stories")
story_count=$(echo "$response" | jq 'length' 2>/dev/null)

if [ "$story_count" = "2" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Found $story_count stories)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 2 stories, Got: $story_count)"
    echo "  Response: $response"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 11: User Isolation
echo -n "Testing: User Isolation (different user) ... "
response=$(curl -s -H "X-User-Id: different_user_999" "$BACKEND_URL/stories")
story_count=$(echo "$response" | jq 'length' 2>/dev/null)

if [ "$story_count" = "0" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Different user has 0 stories)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 0 stories, Got: $story_count)"
    echo "  Response: $response"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 12: Create Story (Invalid JSON)
run_test "Create Story (invalid JSON)" "422" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-User-Id: $TEST_USER_ID" \
    -d 'invalid json' \
    "$BACKEND_URL/stories"

# Test 13: Create Story (Missing Title)
run_test "Create Story (missing title)" "422" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-User-Id: $TEST_USER_ID" \
    -d '{"content":"Content without title"}' \
    "$BACKEND_URL/stories"

# Test 14: API Documentation
run_test "API Documentation (Swagger)" "200" \
    "$BACKEND_URL/docs"

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Test Summary                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ All Tests Passed! 🎉              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ Some Tests Failed                 ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    exit 1
fi
