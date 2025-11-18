# Healthcare AI Application - Current Features Testing Guide

## Prerequisites
- Backend running: `http://localhost:8000`
- Frontend running: `http://localhost:3002`
- Test credentials ready

---

## Test Scenario 1: Patient Journey - PreVisit.ai

### A. Patient Registration & Login
1. Go to `http://localhost:3002/register`
2. Create a new patient account OR use existing:
   - Username: `newpatient`
   - Password: `SecurePass123!`
3. You'll be redirected to `/demo`

### A1. Appointment Prep Summary (NEW - Unified Experience)
1. From patient dashboard at `http://localhost:3002/patient/dashboard`
2. Look for the **"Appointment Preparation"** card (blue border with gradient)
3. Click **"View Appointment Prep Summary"** button
4. **Expected Result**: Unified summary page showing:
   - Your health information
   - Recent symptom analysis (if completed)
   - Personalized discussion topics
   - Medications to confirm
   - Allergies (highlighted in red border)
   - Interactive appointment checklist with progress tracking
5. **Note**: This combines PreVisit.ai symptom analysis + Appoint-Ready context into one patient-friendly view

### B. Symptom Checker
1. Click **"Symptom Checker"** tab
2. Fill in symptom details:
   - **Name**: `Chest pain`
   - **Severity**: `Severe`
   - **Duration**: `30 minutes`
   - **Description**: `Sharp pain in center of chest, radiating to left arm, shortness of breath`
3. Click **"Add Symptom"**
4. Add another symptom:
   - **Name**: `Shortness of breath`
   - **Severity**: `Moderate`
   - **Duration**: `1 hour`
   - **Description**: `Difficulty breathing, feels worse when lying down`
5. Click **"Analyze Symptoms"**
6. **Expected Result**:
   - AI analysis appears with:
     - Urgency level (likely "urgent" or "high")
     - Triage level (1-5, likely 1-2 for these symptoms)
     - Possible conditions (e.g., "Acute Coronary Syndrome", "Myocardial Infarction")
     - Red flags (emergency warnings)
     - Recommendations (e.g., "Seek emergency care immediately")

### C. Medical History Form
1. Click **"Medical History"** tab
2. Complete all 6 steps:

   **Step 1: Allergies**
   - Add: `Penicillin`
   - Add: `Sulfa drugs`
   - Add: `Latex`
   - Click **Next**

   **Step 2: Chronic Conditions**
   - Add: `Diabetes Type 2`
   - Add: `Hypertension`
   - Click **Next**

   **Step 3: Current Medications**
   - Add: `Metformin 1000mg twice daily`
   - Add: `Lisinopril 10mg once daily`
   - Add: `Aspirin 81mg once daily`
   - Click **Next**

   **Step 4: Past Surgeries**
   - Add: `Appendectomy (2015)`
   - Add: `Cholecystectomy (2018)`
   - Click **Next**

   **Step 5: Family History**
   - Add: `Father: Heart disease (age 55, deceased)`
   - Add: `Mother: Diabetes (age 68)`
   - Add: `Brother: Hypertension (age 45)`
   - Click **Next**

   **Step 6: Additional Notes**
   - Add: `Quit smoking 5 years ago. Exercise 3x per week. Occasional alcohol use.`
   - Review summary
   - Click **Complete**

3. **Expected Result**: Success notification, data saved

---

## Test Scenario 2: Provider Journey - Appoint-Ready

### A. Provider Login
1. Logout if logged in as patient
2. Go to `http://localhost:3002/login`
3. Login as doctor:
   - Username: `drjane2`
   - Password: `SecurePass123!`

### B. Access Provider Dashboard
1. After login, go to: `http://localhost:3002/provider/dashboard`
2. **Expected Result**: See provider dashboard with:
   - Stats cards (Patients Today, Pending Tasks, Appoint-Ready, Pending SOAP Notes)
   - Today's Schedule
   - Recent Visits & SOAP Notes section
   - **NEW: Appoint-Ready section at bottom** ⭐

### C. Appoint-Ready Section (NEW - Integrated!)
1. Scroll down to **"Appoint-Ready: Next Patient"** section
2. **Expected Result**: See comprehensive appointment preparation with 3 subsections:

   **Patient Context Card:**
   - Patient: John Doe
   - MRN: MRN-20251102-60640
   - DOB: 1975-06-15 (50 years)
   - Gender: Male
   - Email: newpatient@example.com
   - Address: 123 Main St, Boston, MA 02101
   - Emergency Contact: Jane Doe
   - PreVisit status badge

   **Risk Stratification:**
   - **Cardiovascular Risk**: Score with visual bar
     - Risk factors listed
     - Recommendations provided
   - **Diabetes Risk** (if applicable): Similar structure
   - Color-coded risk levels (Low/Medium/High)

   **Care Gaps:**
   - Typically 7 identified gaps:
     - Annual physical exam
     - Diabetic retinopathy screening
     - Flu vaccination
     - Pneumococcal vaccination
     - Colorectal cancer screening
     - HbA1c testing
     - Lipid panel
   - Each gap shows:
     - Priority badge (Low/Medium/High/Urgent)
     - Overdue status
     - Recommendations

3. **Info Banner**: Blue banner explaining data sources (PreVisit + FHIR)

### D. Alternative: Demo Page Appoint-Ready Tab
1. Go to `http://localhost:3002/demo`
2. Login as provider (`drjane2`)
3. Click **"Appoint-Ready"** tab
4. **Expected Result**: Same Appoint-Ready components in demo view

---

## Test Scenario 3: API Testing (Advanced)

### Test Backend Endpoints Directly

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"newpatient","password":"SecurePass123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"

# 2. Test Symptom Analysis
curl -X POST http://localhost:8000/api/previsit/analyze-symptoms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symptoms": [
      {
        "name": "fever",
        "severity": "moderate",
        "duration": "3 days",
        "description": "Temperature 101F, chills, body aches"
      }
    ]
  }' | python3 -m json.tool

# 3. Test Triage Assessment
curl -X POST http://localhost:8000/api/previsit/triage-assessment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "chief_complaint": "Severe headache with vision changes",
    "vital_signs": {
      "temperature": 98.6,
      "heart_rate": 85,
      "blood_pressure": "140/90",
      "respiratory_rate": 16
    }
  }' | python3 -m json.tool

# 4. Test Questionnaire Generation
curl -X POST http://localhost:8000/api/previsit/generate-questionnaire \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "chief_complaint": "Lower back pain",
    "patient_age": 45
  }' | python3 -m json.tool
```

---

## Test Scenario 4: Role-Based Access Control

### Test Permission Enforcement
1. Login as **patient** (newpatient)
2. Try to access Appoint-Ready tab
3. **Expected Result**: Tab is disabled/grayed out

4. Login as **doctor** (drjane2)
5. Access all tabs
6. **Expected Result**: All tabs accessible

---

## Test Scenario 5: Error Handling

### Test Validation
1. **Symptom Checker**: Try to analyze without adding symptoms
   - **Expected**: Error toast "Please add at least one symptom"

2. **Login**: Try wrong password
   - **Expected**: Error toast "Login failed"

3. **Medical History**: Try to add duplicate items
   - **Expected**: Error toast "This item already exists"

---

## Test Scenario 6: Visit Documentation & SOAP Notes (Provider)

### A. Access Visit Documentation
1. Login as doctor: `drjane2` / `SecurePass123!`
2. Go to provider dashboard: `http://localhost:3002/provider/dashboard`
3. Click **"Document Visit"** on any scheduled appointment
4. **Expected Result**: Visit documentation page loads with:
   - Visit Information card (Patient, Visit Type, Chief Complaint) - ✅ **TEXT NOW VISIBLE**
   - Audio Transcription section
   - SOAP Notes Editor (appears after transcription)

### B. Audio Upload/Recording
1. In Audio Transcription section:
   - Either upload an audio file OR
   - Click "Start Recording" to record live audio
2. Click "Upload" (if file) or "Stop Recording" (if live)
3. **Expected Result**: Audio processes and transcription appears

### C. SOAP Notes Generation
1. After transcription completes, SOAP Notes Editor appears
2. Click **"Generate SOAP Notes"** button
3. **Expected Result**: AI generates structured SOAP notes:
   - **S**ubjective: Patient's complaint in their words
   - **O**bjective: Clinical observations and vital signs
   - **A**ssessment: Diagnosis and clinical reasoning
   - **P**lan: Treatment plan and follow-up

### D. SOAP Notes Refinement
1. Click **Edit** icon on any SOAP section
2. Enter refinement instructions (e.g., "Make more concise")
3. Click **"Refine with AI"**
4. **Expected Result**: Section is refined based on instructions

### E. Save SOAP Notes
1. Review all sections
2. Click **"Save SOAP Notes"**
3. **Expected Result**: Success notification, notes saved to visit

### F. View SOAP Notes Status on Dashboard
1. Return to provider dashboard
2. View **"Recent Visits & SOAP Notes"** section
3. **Expected Result**: See SOAP status for each visit:
   - 🟢 **Complete** - SOAP notes finished
   - 🔵 **In Progress** - SOAP notes started
   - 🟠 **Not Started** - Needs documentation
4. View **"Pending SOAP Notes"** stat card showing count

---

## What's NOT Available Yet

These features are planned but not fully implemented:

### 🔴 Limited Availability:
- ⚠️ **Real-time audio transcription** - Basic functionality exists, Azure Speech Services integration pending
- ⚠️ **Speech-to-text integration** - Mock service only, real Azure integration pending
- ❌ **Live collaboration features** - Multi-provider editing not implemented
- ❌ **Clinical note templates** - Custom templates not yet available
- ❌ **Audio processing optimization** - Using basic processing, advanced features pending

### ✅ AVAILABLE NOW:
- ✅ **SOAP notes generation** - AI-powered generation from transcription
- ✅ **Visit documentation workflow** - Complete workflow implemented
- ✅ **Audio file upload** - Upload .wav, .mp3, .m4a files
- ✅ **Audio recording** - Record audio directly in browser
- ✅ **SOAP notes editing** - Manual editing with AI refinement
- ✅ **Visit status tracking** - Dashboard shows pending documentation

### 📝 Next Implementation Phase:
According to PROJECT_PROGRESS.md, the next steps are:
1. E2E testing setup (Playwright)
2. Comprehensive test suite
3. Azure cloud migration
4. Then: Advanced features (transcription, SOAP notes, etc.)

---

## Success Criteria

You've successfully tested all current features if:
- ✅ Can login as both patient and doctor
- ✅ Can add and analyze symptoms with AI
- ✅ Can complete 6-step medical history form
- ✅ **NEW: Appoint-Ready section visible on provider dashboard** ⭐
- ✅ **NEW: Patient Context Card displays demographics and PreVisit status** ⭐
- ✅ **NEW: Risk Stratification shows cardiovascular and diabetes risk** ⭐
- ✅ **NEW: Care Gaps displays 7 identified gaps with priorities** ⭐
- ✅ Can view patient context (as doctor)
- ✅ Can see risk assessments with scores
- ✅ Can view care gaps with priorities
- ✅ RBAC works (patient can't see Appoint-Ready)
- ✅ All text is readable with good contrast (Visit Info text visibility FIXED)
- ✅ **NEW: Can access unified Appointment Prep Summary from patient dashboard**
- ✅ **NEW: Appointment Prep card is prominently displayed with blue gradient**
- ✅ **NEW: Can view personalized discussion topics and checklist**
- ✅ **NEW: Checklist completion persists in localStorage**
- ✅ Can access visit documentation page
- ✅ Can upload/record audio for transcription
- ✅ Can generate SOAP notes from transcription
- ✅ Can refine SOAP sections with AI
- ✅ Can save SOAP notes to visit
- ✅ Dashboard shows SOAP notes status (provider dashboard)
- ✅ No console errors in browser
