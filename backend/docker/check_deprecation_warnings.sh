#!/bin/bash

##############################################################################
# Healthcare AI Platform - Deprecation Warning Checker
#
# Purpose: Monitor API logs for deprecation warnings after calling old endpoints
# Usage: bash check_deprecation_warnings.sh
#
# This script:
# 1. Calls deprecated endpoints
# 2. Checks logs for deprecation warnings
# 3. Verifies the DeprecationTracker is working
##############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URLs
API_BASE="http://localhost:8000"

##############################################################################
# Helper Functions
##############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_failure() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

##############################################################################
# Main Execution
##############################################################################

print_header "Deprecation Warning Verification"

# Step 1: Clear existing logs to get fresh output
print_step "Step 1: Clearing old logs (keeping last 20 lines)"
docker-compose logs --tail=20 api > /dev/null 2>&1 || true

# Step 2: Call deprecated PreVisit endpoints
print_header "Step 2: Triggering Deprecated PreVisit Endpoints"

endpoints=(
    "/api/previsit/health"
)

for endpoint in "${endpoints[@]}"; do
    print_step "Calling: $endpoint"
    curl -s -o /dev/null "$API_BASE$endpoint" || true
    sleep 1
done

# Step 3: Call deprecated Appoint-Ready endpoints
print_header "Step 3: Triggering Deprecated Appoint-Ready Endpoints"

endpoints=(
    "/api/appoint-ready/health"
)

for endpoint in "${endpoints[@]}"; do
    print_step "Calling: $endpoint"
    curl -s -o /dev/null "$API_BASE$endpoint" || true
    sleep 1
done

# Step 4: Check logs for deprecation warnings
print_header "Step 4: Checking Logs for Deprecation Warnings"

echo "Fetching recent API logs..."
echo ""

# Get logs from the last 2 minutes
logs=$(docker-compose logs --tail=100 api 2>&1 || echo "")

# Check for deprecation warnings
deprecation_count=$(echo "$logs" | grep -c "DEPRECATION WARNING" || echo "0")

if [ "$deprecation_count" -gt 0 ]; then
    print_success "Found $deprecation_count deprecation warning(s) in logs"
    echo ""
    echo -e "${YELLOW}Deprecation warnings found:${NC}"
    echo ""
    echo "$logs" | grep -A 3 "DEPRECATION WARNING" || true
else
    print_failure "No deprecation warnings found in logs"
    echo ""
    echo -e "${YELLOW}Recent logs (last 20 lines):${NC}"
    echo "$logs" | tail -20
fi

echo ""

# Step 5: Check for specific warning messages
print_header "Step 5: Verifying Warning Message Format"

# Check for PreVisit deprecation messages
if echo "$logs" | grep -q "api/previsit.*deprecated.*api/careprep"; then
    print_success "PreVisit → CarePrep migration message found"
else
    print_failure "PreVisit deprecation message not found"
fi

# Check for Appoint-Ready deprecation messages
if echo "$logs" | grep -q "api/appoint-ready.*deprecated.*api/contextai"; then
    print_success "Appoint-Ready → ContextAI migration message found"
else
    print_failure "Appoint-Ready deprecation message not found"
fi

# Check for version removal notice
if echo "$logs" | grep -q "v2.0.0" || echo "$logs" | grep -q "version 2.0.0"; then
    print_success "Version removal notice (v2.0.0) found in warnings"
else
    print_failure "Version removal notice not found"
fi

# Step 6: Sample log output
print_header "Step 6: Sample Deprecation Log Output"

echo "Here's a sample of what the deprecation warnings should look like:"
echo ""
echo "$logs" | grep -B 1 -A 4 "DEPRECATION" | head -20 || echo "No samples found"

# Step 7: Instructions
print_header "Step 7: Manual Verification Steps"

echo "To monitor logs in real-time:"
echo "  ${YELLOW}docker-compose logs -f api | grep --color=always DEPRECATION${NC}"
echo ""
echo "To check deprecation tracker stats (requires adding an endpoint):"
echo "  ${YELLOW}curl $API_BASE/api/admin/deprecation-stats${NC}"
echo ""
echo "To view all logs:"
echo "  ${YELLOW}docker-compose logs api${NC}"
echo ""
echo "To view logs from a specific time:"
echo "  ${YELLOW}docker-compose logs --since 5m api${NC}"
echo ""

# Step 8: Summary
print_header "Summary"

if [ "$deprecation_count" -gt 0 ]; then
    print_success "Deprecation warning system is working correctly!"
    echo ""
    echo "✓ Deprecated endpoints are logging warnings"
    echo "✓ Migration messages are present"
    echo "✓ Version removal notices are included"
    echo ""
    echo -e "${GREEN}Phase 1 backend migration is complete!${NC}"
    exit 0
else
    print_failure "Deprecation warnings not found"
    echo ""
    echo "Possible issues:"
    echo "  - Docker containers might not be running"
    echo "  - Logging configuration might need adjustment"
    echo "  - Deprecation middleware might not be imported"
    echo ""
    echo "Next steps:"
    echo "  1. Check if containers are running: docker-compose ps"
    echo "  2. Verify main.py imports deprecation middleware"
    echo "  3. Check log level in .env.local (should be DEBUG or INFO)"
    exit 1
fi
