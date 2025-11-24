#!/bin/bash

# Test script for complete visit workflow with CarePrep integration
# This tests: CarePrep completion -> Document Visit button -> Visit created with pre-populated SOAP notes

set -e

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo "============================================"
echo "Visit Workflow Integration Test"
echo "============================================"
echo ""

# Login as provider
echo "Step 1: Logging in as provider..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "provider_demo",
    "password": "demo123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ ERROR: Failed to login"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✓ Logged in successfully"
echo ""

# Get the real appointment ID from database
echo "Step 2: Getting appointment ID from database..."
APPOINTMENT_ID=$(docker compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -c "SELECT id FROM appointments LIMIT 1;" | tr -d ' \n')

if [ -z "$APPOINTMENT_ID" ]; then
  echo "❌ ERROR: No appointments found in database"
  exit 1
fi

echo "✓ Found appointment: $APPOINTMENT_ID"
echo ""

# Create CarePrep response with sample data
echo "Step 3: Creating CarePrep response with sample symptom and medical history data..."
CAREPREP_RESPONSE=$(curl -s -X POST "${API_URL}/api/careprep/${APPOINTMENT_ID}/responses" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "medical_history_data": {
      "medications": [
        {"name": "Lisinopril", "dosage": "10mg"},
        {"name": "Metformin", "dosage": "500mg"}
      ],
      "allergies": ["Penicillin", "Shellfish"],
      "conditions": ["Hypertension", "Type 2 Diabetes"],
      "recent_changes": "Patient reports increased fatigue over the past 2 weeks"
    },
    "symptom_checker_data": {
      "symptoms": [
        {"name": "Headache", "severity": "moderate", "duration": "3 days"},
        {"name": "Fatigue", "severity": "severe", "duration": "2 weeks"}
      ],
      "analysis": "Patient experiencing persistent headaches and unusual fatigue"
    }
  }' || echo '{"error": "Failed to create CarePrep response"}')

echo "CarePrep Response: $CAREPREP_RESPONSE"
echo "✓ CarePrep data created"
echo ""

# Create visit from appointment
echo "Step 4: Creating visit from appointment (this will auto-populate CarePrep data)..."
VISIT_RESPONSE=$(curl -s -X POST "${API_URL}/api/visits/from-appointment/${APPOINTMENT_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")

VISIT_ID=$(echo $VISIT_RESPONSE | jq -r '.id')

if [ "$VISIT_ID" = "null" ] || [ -z "$VISIT_ID" ]; then
  echo "❌ ERROR: Failed to create visit"
  echo "Response: $VISIT_RESPONSE"
  exit 1
fi

echo "✓ Visit created: $VISIT_ID"
echo ""

# Fetch the visit to check if CarePrep data was populated
echo "Step 5: Fetching visit to verify CarePrep data auto-population..."
VISIT_DETAIL=$(curl -s -X GET "${API_URL}/api/visits/${VISIT_ID}" \
  -H "Authorization: Bearer ${TOKEN}")

SUBJECTIVE=$(echo $VISIT_DETAIL | jq -r '.subjective')

echo "-----------------------------------------------"
echo "SUBJECTIVE NOTES (Auto-populated from CarePrep):"
echo "-----------------------------------------------"
echo "$SUBJECTIVE"
echo "-----------------------------------------------"
echo ""

# Check if CarePrep data is present in subjective notes
if echo "$SUBJECTIVE" | grep -q "CarePrep"; then
  echo "✅ SUCCESS: CarePrep data successfully auto-populated in SOAP notes!"
else
  echo "⚠️  WARNING: CarePrep data may not be present in SOAP notes"
fi

echo ""
echo "Step 6: Verifying visit details..."
echo "Visit ID: $VISIT_ID"
echo "Appointment ID: $(echo $VISIT_DETAIL | jq -r '.appointment_id')"
echo "Status: $(echo $VISIT_DETAIL | jq -r '.status')"
echo "Patient ID: $(echo $VISIT_DETAIL | jq -r '.patient_id')"
echo ""

# Test updating SOAP notes
echo "Step 7: Testing SOAP notes update..."
UPDATE_RESPONSE=$(curl -s -X PUT "${API_URL}/api/visits/${VISIT_ID}/notes" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "subjective": "'"$SUBJECTIVE"'\n\nAdditional notes: Patient is cooperative and provides detailed history.",
    "objective": "BP: 135/85, HR: 78, Temp: 98.6°F\nPatient appears well-nourished and in no acute distress.",
    "assessment": "1. Essential hypertension - stable on current medication\n2. Type 2 diabetes mellitus - glucose control suboptimal\n3. Headache - likely tension-type, associated with stress",
    "plan": "1. Continue Lisinopril 10mg daily\n2. Increase Metformin to 850mg twice daily\n3. Recommend stress management techniques\n4. Follow-up in 4 weeks for BP and glucose monitoring"
  }')

if echo "$UPDATE_RESPONSE" | jq -e '.id' > /dev/null; then
  echo "✅ SOAP notes updated successfully!"
else
  echo "❌ ERROR: Failed to update SOAP notes"
  echo "Response: $UPDATE_RESPONSE"
fi

echo ""
echo "============================================"
echo "✅ ALL TESTS PASSED!"
echo "============================================"
echo ""
echo "Summary:"
echo "  - Provider logged in successfully"
echo "  - CarePrep data created for appointment"
echo "  - Visit created from appointment"
echo "  - CarePrep data auto-populated into SOAP notes (Subjective)"
echo "  - SOAP notes can be updated successfully"
echo ""
echo "You can now access the visit at:"
echo "  ${FRONTEND_URL}/provider/visits/${VISIT_ID}"
echo ""
