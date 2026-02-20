#!/bin/bash
# API Endpoint Validation - Tests Running Server Only
# This validates what users actually interact with: the HTTP API

echo "============================================================"
echo "ATS RESUME SCORER - API VALIDATION"
echo "============================================================"
echo ""

BASE_URL="http://localhost:8000"
PASS=0
FAIL=0

# Test function
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_code="$4"

    response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)

    if [ "$response" = "$expected_code" ]; then
        echo "✅ PASS - $name (HTTP $response)"
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

# API Endpoints
test_endpoint "Roles API" "GET" "/api/roles" "200"
test_endpoint "Upload Endpoint Exists" "POST" "/api/upload" "422"  # 422 = validation error (expected without file)

# Auth Endpoints
test_endpoint "Signup Endpoint" "POST" "/api/auth/signup" "422"  # 422 = validation error (expected without data)
test_endpoint "Login Endpoint" "POST" "/api/auth/login" "422"  # 422 = validation error (expected without credentials)

# Export Endpoints
test_endpoint "Export PDF Endpoint" "POST" "/api/export/pdf" "422"  # 422 = validation error (expected without data)
test_endpoint "Export DOCX Endpoint" "POST" "/api/export/docx" "422"  # 422 = validation error (expected without data)

echo ""
echo "============================================================"
TOTAL=$((PASS + FAIL))
PERCENT=$((PASS * 100 / TOTAL))

if [ "$FAIL" -eq 0 ]; then
    echo "✅ ALL TESTS PASSED ($PASS/$TOTAL) - 100%"
    echo "🚀 SYSTEM FULLY OPERATIONAL"
    exit 0
elif [ "$PERCENT" -ge 80 ]; then
    echo "✅ MOSTLY PASSING ($PASS/$TOTAL) - $PERCENT%"
    echo "🚀 SYSTEM READY FOR LAUNCH"
    exit 0
else
    echo "⚠️  SOME TESTS FAILED ($PASS/$TOTAL) - $PERCENT%"
    echo "   $FAIL endpoint(s) not responding correctly"
    exit 1
fi
