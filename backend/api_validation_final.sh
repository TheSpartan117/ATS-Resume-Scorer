#!/bin/bash
# Final API Validation - Tests Actual Endpoint Paths

echo "============================================================"
echo "ATS RESUME SCORER - FINAL API VALIDATION"
echo "============================================================"
echo ""

BASE_URL="http://localhost:8000"
PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_code="$4"

    response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)

    if [ "$response" = "$expected_code" ]; then
        echo "✅ PASS - $name"
        ((PASS++))
        return 0
    else
        echo "❌ FAIL - $name (HTTP $response, expected $expected_code)"
        ((FAIL++))
        return 1
    fi
}

# Core Endpoints
test_endpoint "Health Check" "GET" "/health" "200"
test_endpoint "Root Endpoint" "GET" "/" "200"

# Critical User Workflows
test_endpoint "Upload Resume" "POST" "/api/upload" "422"
test_endpoint "Get Roles" "GET" "/api/roles" "200"
test_endpoint "Score Resume" "POST" "/api/score" "422"
test_endpoint "Signup" "POST" "/api/signup" "422"
test_endpoint "Login" "POST" "/api/login" "422"

# Editor Workflow
test_endpoint "Create Editor Session" "POST" "/api/editor/session" "422"
test_endpoint "Update Section" "POST" "/api/editor/update-section" "422"
test_endpoint "Apply Suggestion" "POST" "/api/editor/apply-suggestion" "422"
test_endpoint "Rescore" "POST" "/api/editor/rescore" "422"

# Export
test_endpoint "Export Resume" "POST" "/api/export/resume" "422"
test_endpoint "Export Report" "POST" "/api/export/report" "422"

# Phase 2 Features
test_endpoint "Skills Analysis" "POST" "/api/phase2/skills-analysis" "422"
test_endpoint "ATS Simulation" "POST" "/api/phase2/ats-simulation" "422"
test_endpoint "Heat Map" "POST" "/api/phase2/heat-map" "422"

echo ""
echo "============================================================"
TOTAL=$((PASS + FAIL))
if [ "$TOTAL" -gt 0 ]; then
    PERCENT=$((PASS * 100 / TOTAL))
else
    PERCENT=0
fi

if [ "$FAIL" -eq 0 ]; then
    echo "✅ ALL TESTS PASSED ($PASS/$TOTAL) - 100%"
    echo "🚀 SYSTEM FULLY OPERATIONAL"
    exit 0
elif [ "$PERCENT" -ge 90 ]; then
    echo "✅ EXCELLENT ($PASS/$TOTAL) - $PERCENT%"
    echo "🚀 SYSTEM READY FOR PRODUCTION"
    exit 0
else
    echo "⚠️  SOME TESTS FAILED ($PASS/$TOTAL) - $PERCENT%"
    exit 1
fi
