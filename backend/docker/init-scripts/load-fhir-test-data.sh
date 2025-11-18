#!/bin/bash
# Script to load FHIR test data into HAPI FHIR server

FHIR_SERVER_URL="${FHIR_SERVER_URL:-http://localhost:8081/fhir}"
TEST_DATA_FILE="$(dirname "$0")/fhir-test-data.json"

echo "=========================================="
echo "Loading FHIR Test Data"
echo "=========================================="
echo "FHIR Server: $FHIR_SERVER_URL"
echo "Test Data: $TEST_DATA_FILE"
echo ""

# Wait for FHIR server to be ready
echo "Waiting for FHIR server to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f "${FHIR_SERVER_URL}/metadata" > /dev/null 2>&1; then
        echo "✅ FHIR server is ready!"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Attempt $RETRY_COUNT/$MAX_RETRIES - Server not ready yet..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ ERROR: FHIR server did not become ready in time"
    exit 1
fi

echo ""
echo "Loading test data bundle..."

# Load the FHIR bundle
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d @"$TEST_DATA_FILE" \
    "${FHIR_SERVER_URL}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ Test data loaded successfully (HTTP $HTTP_CODE)"
    echo ""
    echo "Test data includes:"
    echo "  - 2 Patients (John Doe, Jane Smith)"
    echo "  - 2 Conditions (Diabetes Type 2, Hypertension)"
    echo "  - 2 Medications (Metformin, Lisinopril)"
    echo "  - 2 Observations (Blood Glucose, Blood Pressure)"
    echo "  - 1 Allergy (Penicillin)"
    echo ""
    echo "You can verify the data with:"
    echo "  curl ${FHIR_SERVER_URL}/Patient/test-patient-001"
else
    echo "❌ ERROR: Failed to load test data (HTTP $HTTP_CODE)"
    echo "Response:"
    echo "$BODY" | head -20
    exit 1
fi

echo ""
echo "=========================================="
echo "Test data loading complete!"
echo "=========================================="
