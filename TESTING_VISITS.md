# Testing Visits and Transcription Features

This guide explains how to create test visits for testing the doctor's visit interface, including note-taking and transcription features.

## Quick Start

### Option 1: Use the Automated Script (Recommended)

```bash
cd azure-healthcare-app/backend/docker
chmod +x scripts/create_test_visit.sh
./scripts/create_test_visit.sh
```

The script will:
1. Show available patients
2. Prompt you to select a patient by MRN
3. Ask if you want to include a transcript
4. Create an active (IN_PROGRESS) visit with SOAP notes
5. Optionally create a realistic medical transcription

### Option 2: Command Line

```bash
# Create visit for patient MRN001 without transcript
./scripts/create_test_visit.sh MRN001

# Create visit for patient MRN002 with transcript
./scripts/create_test_visit.sh MRN002 transcript
```

## What Gets Created

### 1. Active Visit
- **Status**: `IN_PROGRESS` (visible in doctor's active visits)
- **Patient**: Selected patient from database
- **Provider**: Dr. Sarah Smith (doctor@healthai.com)
- **Visit Type**: Follow-up
- **Chief Complaint**: Follow-up for hypertension management

### 2. SOAP Notes (Partially Filled)

#### Subjective (✅ Filled)
```
Patient reports occasional dizziness when standing up quickly,
occurring 2-3 times daily, mainly in the morning. Denies chest
pain but notes increased fatigue. Taking prescribed antihypertensive
medication regularly with breakfast.
```

#### Objective (✅ Filled)
```
BP: 128/82 mmHg
HR: 72 bpm
Temp: 98.6°F
Weight: 180 lbs
General: Alert and oriented, no acute distress
Cardiovascular: Regular rate and rhythm, no murmurs
```

#### Assessment (⬜ Empty - For Testing)
This section is left empty so you can test adding clinical assessments.

#### Plan (⬜ Empty - For Testing)
This section is left empty so you can test adding treatment plans.

### 3. Medical Transcription (Optional)

If you choose to include a transcript, it contains a realistic doctor-patient conversation:

- **Length**: ~1,500 characters
- **Duration**: 7 minutes (420 seconds)
- **Confidence**: 95%
- **Status**: COMPLETED
- **Content**: Discussion about:
  - Blood pressure medication adjustment
  - Dizziness symptoms (orthostatic hypotension)
  - Dosage reduction (20mg → 10mg)
  - Follow-up planning

**Sample excerpt:**
```
Doctor: Good morning. How have you been feeling since our last visit?

Patient: Good morning, Doctor. I have been taking the medication you
prescribed for my blood pressure, but I have been experiencing some
dizziness, especially when I stand up quickly.

Doctor: I see. How often does this dizziness occur?

Patient: It happens maybe 2-3 times a day, usually in the morning...
```

## Manual Creation Steps

If you prefer to create visits manually or need to understand the process:

### Step 1: Get Patient and Provider IDs

```sql
-- Get patient ID
SELECT id, mrn, first_name, last_name
FROM patients
WHERE mrn = 'MRN001';

-- Get provider ID
SELECT id, email, full_name
FROM users
WHERE role = 'DOCTOR'
LIMIT 1;
```

### Step 2: Create or Get Appointment

```sql
-- Check for existing appointment
SELECT id FROM appointments
WHERE patient_id = 'PATIENT_ID_HERE'
AND status = 'SCHEDULED'
LIMIT 1;

-- Or create new appointment
INSERT INTO appointments (
    id, patient_id, provider_id,
    appointment_type, status,
    scheduled_start, scheduled_end,
    duration_minutes, chief_complaint,
    previsit_completed, created_at, updated_at
) VALUES (
    gen_random_uuid(),
    'PATIENT_ID_HERE',
    'PROVIDER_ID_HERE',
    'FOLLOW_UP',
    'SCHEDULED',
    NOW() - INTERVAL '5 minutes',
    NOW() + INTERVAL '25 minutes',
    30,
    'Follow-up visit',
    'N',
    NOW(),
    NOW()
) RETURNING id;
```

### Step 3: Create Active Visit

```sql
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
    gen_random_uuid(),
    'PATIENT_ID_HERE',
    'PROVIDER_ID_HERE',
    'APPOINTMENT_ID_HERE',
    'FOLLOW_UP',
    'IN_PROGRESS',
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '3 minutes',
    'Follow-up for hypertension management',
    'Patient reports occasional dizziness...',
    'Patient reports occasional dizziness...',
    'BP: 128/82 mmHg
HR: 72 bpm
Temp: 98.6°F
Weight: 180 lbs
General: Alert and oriented, no acute distress
Cardiovascular: Regular rate and rhythm, no murmurs',
    NOW(),
    NOW()
) RETURNING id;
```

### Step 4: Update Appointment Status

```sql
UPDATE appointments
SET status = 'IN_PROGRESS',
    actual_start = NOW() - INTERVAL '3 minutes'
WHERE id = 'APPOINTMENT_ID_HERE';
```

### Step 5: Create Transcript (Optional)

```sql
INSERT INTO transcripts (
    id,
    visit_id,
    transcription_text,
    language,
    confidence_score,
    status,
    audio_duration_seconds,
    started_at,
    completed_at,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'VISIT_ID_HERE',
    'Doctor: Good morning. How have you been feeling...
[Full conversation here]',
    'en',
    95,
    'COMPLETED',
    420,
    NOW() - INTERVAL '2 minutes',
    NOW() - INTERVAL '30 seconds',
    NOW(),
    NOW()
) RETURNING id;
```

## Accessing the Test Visit

### 1. Login to Frontend
```
URL: http://localhost:3000
Email: doctor@healthai.com
Password: Doctor123!
```

### 2. Navigate to Visits
Look for the navigation menu and click on:
- "Visits" or
- "Appointments" or
- "Active Visits"

### 3. Find Your Test Visit
Look for:
- Status: **IN_PROGRESS** (usually highlighted in green)
- Patient name you selected
- Chief complaint: "Follow-up for hypertension management"

### 4. Test Features

Once you open the visit, you can test:

✅ **View Existing SOAP Notes**
- Subjective section (patient history)
- Objective section (vital signs)

✅ **Add/Edit SOAP Notes**
- Add Assessment (clinical impression)
- Add Plan (treatment recommendations)
- Edit existing sections

✅ **View Transcription** (if created)
- Read the full doctor-patient conversation
- See confidence scores
- Review timestamps

✅ **Real-time Updates** (if implemented)
- Save notes
- Auto-save functionality
- Update visit status

## Verifying the Visit

You can verify the visit was created successfully using the API:

```bash
# Get authentication token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor@healthai.com","password":"Doctor123!"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Get provider's visits
curl -s http://localhost:8000/api/visits/provider/PROVIDER_ID_HERE \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Or check the database directly:

```sql
-- View all IN_PROGRESS visits
SELECT
    v.id as visit_id,
    v.status,
    p.first_name || ' ' || p.last_name as patient_name,
    u.full_name as doctor_name,
    v.chief_complaint,
    v.actual_start,
    t.id as transcript_id
FROM visits v
JOIN patients p ON v.patient_id = p.id
JOIN users u ON v.provider_id = u.id
LEFT JOIN transcripts t ON t.visit_id = v.id
WHERE v.status = 'IN_PROGRESS'
ORDER BY v.actual_start DESC;
```

## Cleaning Up Test Data

### Remove Specific Visit

```sql
-- Delete transcript first (if exists)
DELETE FROM transcripts WHERE visit_id = 'VISIT_ID_HERE';

-- Delete visit
DELETE FROM visits WHERE id = 'VISIT_ID_HERE';

-- Optionally reset appointment
UPDATE appointments
SET status = 'SCHEDULED', actual_start = NULL
WHERE id = 'APPOINTMENT_ID_HERE';
```

### Remove All Test Visits

```bash
cd azure-healthcare-app/backend/docker

docker-compose exec postgres psql -U healthcare_user -d healthcare_db -c "
DELETE FROM transcripts WHERE visit_id IN (
    SELECT id FROM visits WHERE status = 'IN_PROGRESS'
);
DELETE FROM visits WHERE status = 'IN_PROGRESS';
UPDATE appointments SET status = 'SCHEDULED', actual_start = NULL
WHERE status = 'IN_PROGRESS';
"
```

## Troubleshooting

### Visit Not Showing in UI

**Problem**: Created visit doesn't appear in the frontend

**Solutions**:
1. Refresh the browser (Ctrl+R or Cmd+R)
2. Check browser console for errors (F12)
3. Verify the visit exists in database:
   ```sql
   SELECT * FROM visits WHERE status = 'IN_PROGRESS';
   ```
4. Check API logs:
   ```bash
   docker-compose logs api | tail -50
   ```

### UUID Validation Errors

**Problem**: API returns UUID validation errors

**Solution**: Always use `gen_random_uuid()` in PostgreSQL or proper UUID format
```sql
-- ✅ CORRECT
id = gen_random_uuid()

-- ❌ WRONG
id = 'test-visit-123'
```

### Transcript Not Showing

**Problem**: Transcript was created but doesn't appear

**Solutions**:
1. Verify transcript is linked to correct visit:
   ```sql
   SELECT visit_id, status, LENGTH(transcription_text)
   FROM transcripts
   WHERE visit_id = 'VISIT_ID_HERE';
   ```
2. Check transcript status is 'COMPLETED'
3. Verify transcription_text is not NULL

### Authentication Issues

**Problem**: Can't access visits API

**Solution**: Get a fresh token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor@healthai.com","password":"Doctor123!"}'
```

## Advanced Testing Scenarios

### Multiple Active Visits

Create visits for different patients to test:
```bash
./scripts/create_test_visit.sh MRN001 transcript
./scripts/create_test_visit.sh MRN002 transcript
```

### Different Visit Types

Modify the script or SQL to create different visit types:
- `INITIAL_CONSULTATION`
- `FOLLOW_UP`
- `URGENT_CARE`
- `ANNUAL_PHYSICAL`

### Completed Visits

Change status to test visit history:
```sql
UPDATE visits
SET status = 'COMPLETED',
    actual_end = NOW()
WHERE id = 'VISIT_ID_HERE';
```

## Summary

The automated script (`create_test_visit.sh`) is the easiest way to create test visits. It:
- ✅ Handles all UUID generation automatically
- ✅ Validates patient and provider exist
- ✅ Creates proper foreign key relationships
- ✅ Generates realistic medical data
- ✅ Supports both with and without transcripts
- ✅ Provides clear output and confirmation

For production use, visits would be created through:
- API endpoints (`POST /api/visits`)
- Doctor's UI when starting an appointment
- Automated scheduling systems
- FHIR integration

This testing setup allows you to develop and test the visit interface without needing the full appointment workflow!
