# Testing the Complete Visit Workflow

## Prerequisites
- All Docker containers running
- Fresh login token (login within the last 30 minutes)

## Step-by-Step Testing Guide

### Step 1: Login to Provider Dashboard

1. Open browser and go to: http://localhost:3000/login
2. Login with credentials:
   - **Username**: `provider_demo`
   - **Password**: `demo123`
3. You should be redirected to: http://localhost:3000/provider/dashboard

### Step 2: View Today's Schedule

On the provider dashboard, you should see:
- "Today's Schedule" section with 3 mock appointments
- Each appointment shows:
  - Time (e.g., "09:00 AM")
  - Patient name (e.g., "John Doe")
  - Reason for visit
  - **CarePrep Status Badge** (Complete/In Progress/Not Started)
  - Two buttons:
    - **"CarePrep Link"** - Copy link to share with patient
    - **"Document Visit"** - Start visit documentation

### Step 3: Click "Document Visit"

1. Click the **"Document Visit"** button on any appointment
2. You should see:
   - Button changes to "Creating..." with a spinner
   - A success toast: "Visit created with CarePrep data pre-populated!"
   - Browser navigates to: `/provider/visits/[VISIT_ID]`

### Step 4: Verify Visit Page Loads

On the visit documentation page, you should see:

**Visit Information Card**:
- Patient Name: John Doe (or the patient from the appointment)
- Visit Type: Follow-up
- Status: In Progress (blue badge)
- Chief Complaint: "Follow-up on diabetes management..."

**SOAP Notes Editor**:
- 4 sections: Subjective, Objective, Assessment, Plan
- Subjective field should be **PRE-POPULATED** with CarePrep data like:
  ```
  Chief Complaint: Follow-up on diabetes management and recent lab results
  ```

### Step 5: Complete the SOAP Notes

1. **Subjective**: Already populated from CarePrep - review and add more if needed
2. **Objective**: Add examination findings, e.g.:
   ```
   BP: 135/85, HR: 78, Temp: 98.6°F
   Patient appears well-nourished and in no acute distress.
   ```
3. **Assessment**: Add diagnoses, e.g.:
   ```
   1. Essential hypertension - stable on current medication
   2. Type 2 diabetes mellitus - glucose control suboptimal
   ```
4. **Plan**: Add treatment plan, e.g.:
   ```
   1. Continue Lisinopril 10mg daily
   2. Increase Metformin to 850mg twice daily
   3. Follow-up in 4 weeks for BP and glucose monitoring
   ```

### Step 6: Save the Visit

1. Click **"Save Notes"** button (top right)
2. You should see:
   - Success toast: "SOAP notes saved successfully!"
   - Notes are saved to the database

### Step 7: Verify Data Persistence

1. Refresh the page (F5)
2. All your SOAP notes should still be there
3. The visit status remains "In Progress"

---

## Troubleshooting

### Error: "Could not validate credentials: Not enough segments"

**Cause**: Your authentication token is expired or invalid.

**Solution**:
1. Clear browser storage:
   - Press F12 → Application tab → Local Storage
   - Delete `token` entry
2. Go to http://localhost:3000/login
3. Log in again with `provider_demo` / `demo123`

**Or run this in browser console**:
```javascript
localStorage.clear();
window.location.href = '/login';
```

### Error: "Visit not found"

**Cause**: The visit ID doesn't exist in the database.

**Solution**: Create a new visit by clicking "Document Visit" on the dashboard.

### Error: "Failed to load visit"

**Cause**: Could be network issue or backend down.

**Solution**:
1. Check backend is running: `docker compose ps`
2. Check backend logs: `docker compose logs api | tail -50`
3. Verify API is accessible: `curl http://localhost:8000/health`

---

## Expected Behavior Summary

✅ **What Should Work**:
1. Login redirects to provider dashboard
2. Dashboard shows today's appointments with CarePrep status
3. "Document Visit" creates a new visit and navigates to visit page
4. Visit page loads with patient info and pre-populated Subjective notes
5. Provider can edit all SOAP sections
6. "Save Notes" persists changes to database
7. Refresh maintains all saved data

✅ **CarePrep Integration**:
- If patient completed CarePrep, Subjective field includes:
  - Symptoms with severity and duration
  - Current medications
  - Allergies
  - Chronic conditions
  - Recent health changes

✅ **Authentication Handling**:
- Expired tokens automatically redirect to login
- Missing tokens show friendly error messages
- 401 errors clear localStorage and redirect after 2 seconds

---

## Testing with Real CarePrep Data

To test the complete workflow with actual CarePrep data:

### Option 1: Use the Test Script

```bash
cd backend/docker
./test_visit_workflow.sh
```

This will:
- Create a visit with mock CarePrep data
- Verify auto-population works
- Print the visit URL you can access

### Option 2: Manual Testing via API

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "provider_demo", "password": "demo123"}' | jq -r '.access_token')

# 2. Get appointment ID
APPT_ID=$(docker compose exec -T postgres psql -U healthcare_user -d healthcare_db -t -c "SELECT id FROM appointments LIMIT 1;" | tr -d ' \n')

# 3. Create visit from appointment
VISIT=$(curl -s -X POST "http://localhost:8000/api/visits/from-appointment/${APPT_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json")

echo $VISIT | jq '.subjective'
```

---

## Next Steps After Testing

Once you've verified the workflow works:

1. **Test Edge Cases**:
   - Create visit without CarePrep data (should still work)
   - Edit and save multiple times
   - Test with different appointment types

2. **Performance Testing**:
   - Create multiple visits
   - Check database query performance
   - Monitor API response times

3. **Security Testing**:
   - Verify only providers can create visits
   - Test cross-user access prevention
   - Validate HIPAA compliance measures

4. **Future Enhancements**:
   - Add voice transcription integration
   - Implement AI SOAP note generation
   - Add template support for common visit types
   - Enable collaborative editing for multiple providers
