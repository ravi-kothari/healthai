# Testing Guide: Appoint-Ready Features

## Current Setup Status

✅ **Frontend**: Running on http://localhost:3000 (PID: 56631)
✅ **Backend**: Mock server running on http://localhost:8000 (PID: 57160)
✅ **All 8 Appoint-Ready Endpoints**: Working correctly

## How to Test

### 1. Login
1. Navigate to: http://localhost:3000
2. Click "Login" or navigate to http://localhost:3000/login
3. Enter credentials:
   - Username: `doctor` (or `provider`)
   - Password: `anything` (any password works)
4. Click "Sign In"

### 2. Access Provider Dashboard
- After login, you should be redirected to: http://localhost:3000/provider/dashboard
- OR manually navigate there after logging in

### 3. What You Should See

#### Top Section:
- **Header**: "Provider Dashboard" with "Welcome back, {your name}"
- **4 Stats Cards**: Patients Today, Pending Tasks, ContextAI, SOAP Notes
- **My Templates Card**: Shows template count

#### Middle Section:
- **Today's Schedule**: List of 4 appointments
- **Recent Visits & SOAP Notes**: 3 recent visits

#### Right Sidebar:
- **Patient Watchlist**: 3 patients with ContextAI status
- **Pending Tasks**: 3 tasks
- **Quick Templates**: Recently used templates

#### Bottom Section - THIS IS WHERE APPOINT-READY FEATURES ARE:

**ContextAI: Next Patient** section should display:

1. **Appointment Info Card** (Blue background):
   - Patient: John Doe (MRN: MRN-123456)
   - Chief Complaint: Annual checkup
   - CarePrep Status: Completed

2. **Patient Context Card**:
   - Demographics (Age: 45, Gender: male)
   - Active Medications (2): Lisinopril 10mg, Metformin 500mg
   - Active Conditions (2): Hypertension, Type 2 Diabetes
   - Allergies (1): Penicillin - Rash (moderate)
   - Recent Vitals

3. **Risk Stratification Card**:
   - Overall Risk Score: 65 (Moderate)
   - Cardiovascular Risk: 70
     - Factors: Hypertension, Elevated LDL
     - Recommendations: Lifestyle modifications, Consider statin therapy
   - Metabolic Risk: 75
     - Factors: Type 2 Diabetes, Elevated A1C
     - Recommendations: Diabetes management, Dietary counseling

4. **Care Gaps Card**:
   - 2 Care Gaps identified
   - Gap 1: Annual flu vaccine (Overdue) - High priority
   - Gap 2: Diabetic retinopathy screening (Upcoming) - Medium priority

5. **Key Test Results Card**:
   - Filter: "All Results" / "Abnormal Only"
   - 3 Test Results:
     - **Hemoglobin A1C**: 7.2% (↔ stable) - ABNORMAL HIGH (yellow badge)
     - **LDL Cholesterol**: 145 mg/dL (↑ up) - ABNORMAL HIGH (yellow badge)
     - **Creatinine**: 1.1 mg/dL (↔ stable) - NORMAL (green badge)
   - Summary: 2 abnormal, 0 critical

6. **Medication Review Card**:
   - Active Medications (2):
     - Lisinopril 10mg - Once daily
     - Metformin 500mg - Twice daily
   - Drug Interactions (1):
     - Lisinopril + Metformin
     - Severity: MILD (blue border)
     - Description: May increase risk of hypoglycemia
     - Recommendation: Monitor blood glucose levels regularly
   - Allergy Alert: Penicillin - Rash (moderate)

## Troubleshooting

### If you DON'T see the ContextAI section:
1. Make sure you're logged in
2. Check that the mock backend is running: `lsof -i :8000`
3. Open browser DevTools (F12) → Console tab → Look for errors
4. Check Network tab → Look for failed API calls

### If you see "No Upcoming Appointments":
1. The `/api/appointments/next` endpoint might be failing
2. Test it manually:
   ```bash
   # Get token first
   TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"doctor","password":"test"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

   # Test appointment endpoint
   curl -s http://localhost:8000/api/appointments/next \
     -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
   ```

### If you see appointment but no feature cards:
1. Open browser DevTools → Console → Look for JavaScript errors
2. Check Network tab → Filter by "appoint-ready" → See which API calls are failing
3. Test endpoints manually using the script:
   ```bash
   cd /Users/ravi/Documents/gemini_projects/Healthcare/azure-healthcare-app/backend
   bash test_all_endpoints.sh
   ```

### Common Issues:

**Issue**: Login doesn't work
**Solution**: Make sure mock backend is running on port 8000
```bash
lsof -i :8000
# If nothing, restart it:
cd /Users/ravi/Documents/gemini_projects/Healthcare/azure-healthcare-app/backend
python3 simple_mock.py
```

**Issue**: Features not loading
**Solution**: Check browser console for errors, verify API calls in Network tab

**Issue**: Blank page after login
**Solution**:
1. Check frontend logs: `tail -f /tmp/frontend.log`
2. Restart frontend: Kill process 56631 and restart with `npm run dev`

## All 8 Appoint-Ready Features Checklist

When you access the dashboard, you should see ALL of these:

- [ ] 1. **Appointment context preparation** - Patient Context Card showing demographics, meds, conditions
- [ ] 2. **Visit summary generation** - EHR data displayed in Patient Context Card
- [ ] 3. **Clinical decision support recommendations** - Risk Stratification recommendations
- [ ] 4. **Patient context cards** - Patient Context Card component
- [ ] 5. **Pre-visit risk stratification scoring** - Risk Stratification Card with score 65
- [ ] 6. **Care gap identification** - Care Gaps Card showing 2 gaps
- [ ] 7. **Relevant test results highlighting** - Key Test Results Card with 3 results
- [ ] 8. **Medication interaction checking** - Medication Review Card with 1 interaction

## Screenshots Location

When testing, if you want to share what you're seeing, take screenshots of:
1. Full dashboard page (scroll to capture all)
2. The "ContextAI: Next Patient" section specifically
3. Browser DevTools Console (if there are errors)
4. Browser DevTools Network tab filtered to "appoint-ready"

## Need Help?

Run this diagnostic script:
```bash
cd /Users/ravi/Documents/gemini_projects/Healthcare/azure-healthcare-app/backend
bash test_all_endpoints.sh
```

This will test all backend endpoints and confirm they're working.
