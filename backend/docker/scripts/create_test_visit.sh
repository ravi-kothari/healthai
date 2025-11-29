#!/bin/bash

################################################################################
# Create Test Visit Script
#
# This script creates an active (IN_PROGRESS) visit with a transcript for
# testing the doctor's visit interface, note-taking, and transcription features.
#
# Usage:
#   ./create_test_visit.sh [patient_mrn] [optional: with-transcript]
#
# Examples:
#   ./create_test_visit.sh MRN001              # Create visit for patient MRN001
#   ./create_test_visit.sh MRN002 transcript   # Create visit with transcript
#   ./create_test_visit.sh                     # Interactive mode (prompts for input)
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Create Test Visit Script${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Change to docker directory
cd "$DOCKER_DIR"

# Check if docker-compose is running
if ! docker-compose ps | grep -q "healthcare-postgres.*Up"; then
    echo -e "${RED}❌ Error: Docker services are not running${NC}"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

# Function to get patients
get_patients() {
    echo -e "${BLUE}Available Patients:${NC}"
    docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db << 'EOF'
SELECT
    ROW_NUMBER() OVER (ORDER BY created_at) as num,
    id,
    mrn,
    first_name || ' ' || last_name as name,
    date_of_birth
FROM patients
ORDER BY created_at;
EOF
}

# Function to get provider
get_provider() {
    docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c \
        "SELECT id FROM users WHERE role = 'DOCTOR' LIMIT 1;"
}

# Interactive mode if no arguments
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Interactive Mode${NC}"
    echo ""

    get_patients

    echo ""
    read -p "Enter patient MRN (e.g., MRN001): " PATIENT_MRN

    echo ""
    read -p "Create with transcript? (y/n): " CREATE_TRANSCRIPT

else
    # Command line mode
    PATIENT_MRN="$1"

    if [ "$2" = "transcript" ] || [ "$2" = "with-transcript" ]; then
        CREATE_TRANSCRIPT="y"
    else
        CREATE_TRANSCRIPT="n"
    fi
fi

echo ""
echo -e "${BLUE}Creating test visit...${NC}"

# Get patient ID from MRN
PATIENT_ID=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c \
    "SELECT id FROM patients WHERE mrn = '$PATIENT_MRN' LIMIT 1;")

if [ -z "$PATIENT_ID" ]; then
    echo -e "${RED}❌ Error: Patient with MRN '$PATIENT_MRN' not found${NC}"
    exit 1
fi

# Get patient name
PATIENT_NAME=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c \
    "SELECT first_name || ' ' || last_name FROM patients WHERE mrn = '$PATIENT_MRN';")

# Get provider ID
PROVIDER_ID=$(get_provider)

if [ -z "$PROVIDER_ID" ]; then
    echo -e "${RED}❌ Error: No doctor/provider found in database${NC}"
    exit 1
fi

# Get provider name
PROVIDER_NAME=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c \
    "SELECT full_name FROM users WHERE id = '$PROVIDER_ID';")

# Get or create appointment
APPOINTMENT_ID=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c \
    "SELECT id FROM appointments WHERE patient_id = '$PATIENT_ID' AND status = 'SCHEDULED' LIMIT 1;" 2>/dev/null | head -n 1)

if [ -z "$APPOINTMENT_ID" ]; then
    echo -e "${YELLOW}No scheduled appointment found. Creating one...${NC}"

    APPOINTMENT_ID=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c \
        "INSERT INTO appointments (
            id, patient_id, provider_id, appointment_type, status,
            scheduled_start, scheduled_end, duration_minutes,
            chief_complaint, previsit_completed, created_at, updated_at
        ) VALUES (
            gen_random_uuid()::text,
            '$PATIENT_ID',
            '$PROVIDER_ID',
            'FOLLOW_UP',
            'SCHEDULED',
            NOW() - INTERVAL '5 minutes',
            NOW() + INTERVAL '25 minutes',
            30,
            'Follow-up visit for ongoing care',
            'N',
            NOW(),
            NOW()
        ) RETURNING id;" 2>/dev/null | head -n 1)
fi

# Create the visit
echo -e "${BLUE}Creating visit for: ${PATIENT_NAME}${NC}"

VISIT_ID=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c "
INSERT INTO visits (
    id,
    patient_id,
    provider_id,
    appointment_id,
    visit_type,
    status,
    scheduled_start,
    actual_start,
    chief_complaint,
    reason_for_visit,
    subjective,
    objective,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid()::text,
    '$PATIENT_ID',
    '$PROVIDER_ID',
    '$APPOINTMENT_ID',
    'FOLLOW_UP',
    'IN_PROGRESS',
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '3 minutes',
    'Follow-up for hypertension management',
    'Patient reports occasional dizziness when standing up quickly, occurring 2-3 times daily, mainly in the morning. Denies chest pain but notes increased fatigue. Taking prescribed antihypertensive medication regularly with breakfast.',
    'Patient reports occasional dizziness when standing up quickly, occurring 2-3 times daily, mainly in the morning. Denies chest pain but notes increased fatigue. Taking prescribed antihypertensive medication regularly with breakfast.',
    'BP: 128/82 mmHg, HR: 72 bpm, Temp: 98.6°F, Weight: 180 lbs. General: Alert and oriented, no acute distress. Cardiovascular: Regular rate and rhythm, no murmurs',
    NOW(),
    NOW()
)
RETURNING id;
" 2>/dev/null | head -n 1)

# Update appointment to IN_PROGRESS
docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -c \
    "UPDATE appointments SET status = 'IN_PROGRESS', actual_start = NOW() - INTERVAL '3 minutes' WHERE id = '$APPOINTMENT_ID';" > /dev/null

echo -e "${GREEN}✓ Visit created successfully!${NC}"
echo -e "  Visit ID: ${YELLOW}$VISIT_ID${NC}"

# Create transcript if requested
if [ "$CREATE_TRANSCRIPT" = "y" ] || [ "$CREATE_TRANSCRIPT" = "yes" ]; then
    echo ""
    echo -e "${BLUE}Creating transcript...${NC}"

    TRANSCRIPT_ID=$(docker-compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -A -c "INSERT INTO transcripts (id, visit_id, transcription_text, language, confidence_score, status, audio_duration_seconds, started_at, completed_at, created_at, updated_at) VALUES (gen_random_uuid()::text, '$VISIT_ID', 'Doctor: Good morning. How have you been feeling since our last visit? Patient: Good morning, Doctor. I have been taking the medication you prescribed for my blood pressure, but I have been experiencing some dizziness, especially when I stand up quickly. Doctor: I see. How often does this dizziness occur? Patient: It happens maybe 2-3 times a day, usually in the morning or when I get up from sitting. Doctor: Are you experiencing any other symptoms? Headaches, fatigue, or chest pain? Patient: No chest pain, but I do feel a bit more tired than usual. Doctor: Let me check your blood pressure. Your reading is 128/82, which is better than last time, but the dizziness suggests we might need to adjust the dosage slightly. Patient: So is that what is causing the dizziness? Doctor: Possibly. The medication might be lowering your blood pressure a bit too much when you stand up. This is called orthostatic hypotension. I am going to reduce your dosage from 20mg to 10mg and we will monitor it for the next two weeks. Patient: Will that help with the tiredness too? Doctor: It should. The fatigue could also be related to the medication. I also want you to make sure you are drinking plenty of water and standing up slowly, especially in the morning. Patient: Okay, I can do that. Should I come back in two weeks? Doctor: Yes, let us schedule a follow-up in two weeks. In the meantime, if the dizziness gets worse or you experience any chest pain or severe headaches, call the office immediately. Patient: I understand. Thank you, Doctor.', 'en', 95, 'COMPLETED', 420, NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '30 seconds', NOW(), NOW()) RETURNING id;" 2>/dev/null | head -n 1)

    echo -e "${GREEN}✓ Transcript created successfully!${NC}"
    echo -e "  Transcript ID: ${YELLOW}$TRANSCRIPT_ID${NC}"
fi

# Display summary
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Test Visit Created!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}Visit Details:${NC}"
echo -e "  Patient: ${YELLOW}$PATIENT_NAME${NC} (MRN: $PATIENT_MRN)"
echo -e "  Provider: ${YELLOW}$PROVIDER_NAME${NC}"
echo -e "  Visit ID: ${YELLOW}$VISIT_ID${NC}"
echo -e "  Status: ${GREEN}IN_PROGRESS${NC}"
echo -e "  Chief Complaint: Follow-up for hypertension management"
echo ""
echo -e "${BLUE}What's Included:${NC}"
echo -e "  ✅ SOAP Notes - Subjective section"
echo -e "  ✅ SOAP Notes - Objective section (vital signs)"
echo -e "  ⬜ SOAP Notes - Assessment (empty for testing)"
echo -e "  ⬜ SOAP Notes - Plan (empty for testing)"
if [ "$CREATE_TRANSCRIPT" = "y" ] || [ "$CREATE_TRANSCRIPT" = "yes" ]; then
    echo -e "  ✅ Medical transcription (1,500+ characters)"
fi
echo ""
echo -e "${BLUE}How to Access:${NC}"
echo -e "  1. Login at http://localhost:3000"
echo -e "     Email: ${YELLOW}doctor@healthai.com${NC}"
echo -e "     Password: ${YELLOW}Doctor123!${NC}"
echo -e "  2. Navigate to Visits/Appointments"
echo -e "  3. Look for ${GREEN}IN_PROGRESS${NC} visit for ${YELLOW}$PATIENT_NAME${NC}"
echo ""
echo -e "${GREEN}Ready to test! 🎉${NC}"
