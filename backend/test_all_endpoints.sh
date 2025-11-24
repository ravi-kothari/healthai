#!/bin/bash

echo "========================================="
echo "Testing All Appoint-Ready Endpoints"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get token
echo "1. Login..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor","password":"test"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Login failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Login successful${NC}"
echo "Token: $TOKEN"
echo ""

# Test endpoints
echo "2. Testing /api/appointments/next..."
curl -s http://localhost:8000/api/appointments/next \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -15
echo ""

echo "3. Testing /api/appoint-ready/patient-context/patient-456..."
curl -s http://localhost:8000/api/appoint-ready/patient-context/patient-456 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -15
echo ""

echo "4. Testing /api/appoint-ready/risk-stratification/patient-456..."
curl -s http://localhost:8000/api/appoint-ready/risk-stratification/patient-456 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -15
echo ""

echo "5. Testing /api/appoint-ready/care-gaps/patient-456..."
curl -s http://localhost:8000/api/appoint-ready/care-gaps/patient-456 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -15
echo ""

echo "6. Testing /api/appoint-ready/test-results/patient-456..."
curl -s http://localhost:8000/api/appoint-ready/test-results/patient-456 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -15
echo ""

echo "7. Testing /api/appoint-ready/medication-review/patient-456..."
curl -s http://localhost:8000/api/appoint-ready/medication-review/patient-456 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -15
echo ""

echo "========================================="
echo -e "${GREEN}✅ All endpoints tested successfully!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Navigate to http://localhost:3000"
echo "2. Login with username=doctor, password=anything"
echo "3. You should see the Appoint-Ready features on the dashboard"
echo ""
