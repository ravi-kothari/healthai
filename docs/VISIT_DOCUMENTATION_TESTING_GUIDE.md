# Visit Documentation Testing Guide
## Audio Transcription & SOAP Notes Generation

This guide walks you through testing the newly implemented Visit Documentation features including audio transcription and AI-powered SOAP notes generation.

---

## Prerequisites

- ✅ Backend running: `http://localhost:8000`
- ✅ Frontend running: `http://localhost:3002`
- ✅ Test visit created in database
- ✅ Test credentials ready

---

## Test Scenario 1: Audio Transcription Workflow

### A. Provider Login
1. Go to `http://localhost:3002/login`
2. Login as doctor:
   - **Username**: `drjane2`
   - **Password**: `SecurePass123!`
3. You'll be redirected to `/demo`
4. Click on the **"Visit Docs"** tab

### B. Upload Audio File

1. **Prepare Test Audio** (Option 1):
   - Create a simple test audio file (WAV/MP3)
   - Or download a sample medical consultation audio
   - File should be under 50MB

2. **Upload Audio**:
   - Click the file input under "Upload Audio File"
   - Select your audio file
   - Click **"Upload"** button

3. **Expected Result**:
   - Toast notification: "Audio uploaded and transcription started!"
   - File appears in "Transcriptions" section with status "Processing"
   - After processing completes (a few seconds), status changes to "Completed"
   - Transcription text appears in a gray box

### C. Record Audio (Option 2)

1. **Start Recording**:
   - Click **"Start Recording"** button
   - Allow microphone access when prompted
   - Red recording indicator appears

2. **Speak Medical Content** (example):
   ```
   "Patient presents with chief complaint of headache for 3 days.
   Pain is localized to the frontal region, described as dull and constant,
   rated 6 out of 10 in severity. Associated symptoms include
   photophobia and mild nausea. No vomiting, no fever, no neck stiffness.
   Patient has tried over-the-counter ibuprofen with minimal relief."
   ```

3. **Stop Recording**:
   - Click **"Stop Recording"** button
   - Toast notification: "Recording saved. Click Upload to transcribe."
   - File name shows in the selected file area

4. **Upload Recording**:
   - Click **"Upload"** button
   - Processing begins automatically

5. **Expected Result**:
   - Mock transcription appears with medical context
   - Confidence score shown (95%)
   - Duration displayed in seconds

---

## Test Scenario 2: SOAP Notes Generation

### A. Generate SOAP Notes from Transcription

1. **Navigate to SOAP Notes Tab**:
   - After successful transcription, click the **"SOAP Notes"** tab in Visit Documentation
   - Or manually click the SOAP Notes tab

2. **Generate Notes**:
   - Click **"Generate from Transcription"** button
   - Loading indicator appears: "Generating..."

3. **Expected Result**:
   - All four SOAP sections populate automatically:
     - **Subjective (S)**: Patient's symptoms in their words
     - **Objective (O)**: Clinical findings and exam results
     - **Assessment (A)**: Medical diagnoses
     - **Plan (P)**: Treatment plan and follow-up
   - Additional cards appear below:
     - **Diagnoses**: Badge list of diagnoses
     - **Medications**: List of prescribed medications
     - **Red Flags**: Warning signs (if any)
     - **Vital Signs**: Vital signs grid (if available)
   - Toast notification: "SOAP notes generated successfully!"

### B. Edit SOAP Sections

1. **Manual Editing**:
   - Click in any SOAP section textarea
   - Type or modify the text directly
   - Changes are reflected immediately

2. **AI-Powered Refinement**:
   - Click the **Edit** icon (pencil) next to any section title
   - Blue refinement panel appears
   - Enter refinement instructions, for example:
     - "Make this more concise"
     - "Add more detail about symptoms"
     - "Use simpler language for patient understanding"
   - Click **"Refine with AI"** button

3. **Expected Result**:
   - Loading indicator: "Refining..."
   - Section updates with refined text
   - Toast notification: "SUBJECTIVE section refined successfully!"
   - Edit panel closes automatically

### C. Save SOAP Notes

1. **Save Documentation**:
   - Review all sections
   - Make any final edits
   - Click **"Save Notes"** button at the top

2. **Expected Result**:
   - Loading indicator: "Saving..."
   - Toast notification: "SOAP notes saved successfully!"
   - Notes are persisted to the visit record in database

---

## Test Scenario 3: Complete Visit Documentation Workflow

### A. End-to-End Test

1. **Start Visit** (Already done via setup script):
   - Visit status: `IN_PROGRESS`
   - Visit ID: `84fc2847-fcca-438f-884c-50c8c660561d`

2. **Upload/Record Audio**:
   - Follow steps from Test Scenario 1
   - Verify transcription completes successfully

3. **Generate SOAP Notes**:
   - Click "Generate from Transcription"
   - Verify all sections populate

4. **Refine Sections**:
   - Test AI refinement on at least 2 sections
   - Try different refinement instructions:
     - "Make this section more detailed"
     - "Simplify the medical terminology"
     - "Add bullet points for clarity"

5. **Save Documentation**:
   - Save the SOAP notes
   - Verify success notification

6. **Verify Persistence**:
   - Refresh the page
   - Navigate back to "Visit Docs" tab
   - SOAP Notes tab should still show saved content

### B. Verify Backend API

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"drjane2","password":"SecurePass123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Get visit details to verify saved SOAP notes
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/visits/84fc2847-fcca-438f-884c-50c8c660561d \
  | python3 -m json.tool
```

**Expected Output**:
```json
{
  "id": "84fc2847-fcca-438f-884c-50c8c660561d",
  "patient_id": "516439f3-7727-44e6-b23d-18ec5249e865",
  "provider_id": "3e470398-c8fc-40ac-80e3-b908df3d6fbf",
  "visit_type": "in_person",
  "status": "IN_PROGRESS",
  "chief_complaint": "Headache for 3 days",
  "subjective": "Patient presents with headache...",
  "objective": "Blood pressure 120/80...",
  "assessment": "Migraine headache...",
  "plan": "Prescribe sumatriptan...",
  "transcripts": [
    {
      "id": "...",
      "transcription_text": "Patient presents with...",
      "status": "COMPLETED",
      "confidence_score": 95
    }
  ]
}
```

---

## Test Scenario 4: Multiple Transcriptions

### A. Upload Multiple Audio Files

1. **First Audio Upload**:
   - Upload first audio file
   - Wait for transcription to complete

2. **Second Audio Upload**:
   - Upload another audio file
   - Wait for transcription

3. **Expected Result**:
   - Both transcriptions appear in the list
   - Ordered by creation time (most recent first)
   - Each has its own status badge
   - Each shows confidence score and duration

### B. Generate SOAP from Specific Transcription

1. **With Multiple Transcriptions**:
   - Generate SOAP notes
   - System automatically uses the most recent transcription

2. **Verify Behavior**:
   - SOAP notes reflect content from latest transcription
   - Auto-save feature updates visit notes if visit is IN_PROGRESS

---

## Test Scenario 5: Error Handling

### A. Test File Size Limit

1. **Large File Upload**:
   - Try to upload a file larger than 50MB
   - **Expected**: Error toast "File size must be less than 50MB"

### B. Test Invalid File Type

1. **Wrong File Format**:
   - Try to upload a non-audio file (e.g., PDF, image)
   - **Expected**: Error toast "Please select a valid audio file (WAV, MP3, WebM, OGG)"

### C. Test Generation Without Transcription

1. **No Transcriptions**:
   - Create a new visit (run setup script again)
   - Navigate to SOAP Notes tab
   - Try to generate SOAP notes
   - **Expected**: Error toast "No transcriptions found for this visit"

### D. Test Refinement Without Instructions

1. **Empty Refinement**:
   - Click edit icon on a section
   - Leave refinement instructions empty
   - Click "Refine with AI"
   - **Expected**: Error toast "Please provide refinement instructions"

---

## Test Scenario 6: Role-Based Access Control

### A. Test as Patient

1. **Login as Patient**:
   - Logout from doctor account
   - Login with patient credentials:
     - Username: `newpatient`
     - Password: `SecurePass123!`

2. **Try to Access Visit Docs**:
   - Navigate to demo page
   - "Visit Docs" tab should be **disabled** (grayed out)
   - Click on it

3. **Expected Result**:
   - Message: "Visit documentation features are only available to healthcare providers"

### B. Test API Access

```bash
# Login as patient
PATIENT_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"newpatient","password":"SecurePass123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Try to create transcription (should fail)
curl -X POST http://localhost:8000/api/visits/84fc2847-fcca-438f-884c-50c8c660561d/transcriptions \
  -H "Authorization: Bearer $PATIENT_TOKEN" \
  -F "audio_file=@test.wav"
```

**Expected**: 403 Forbidden - "Only providers can create transcriptions"

---

## Test Scenario 7: Mock vs Real AI Services

### A. Current Setup (Mock Mode)

The system is currently using **mock AI services** for local development:
- `USE_MOCK_OPENAI=true` - Mock GPT-4o responses
- `USE_MOCK_SPEECH=true` - Mock transcription service

### B. Mock Behavior

1. **Mock Speech Service**:
   - Returns predefined medical transcription text
   - Always returns 95% confidence
   - Duration calculated based on file size

2. **Mock OpenAI Service**:
   - Detects intent from prompts
   - Returns structured SOAP notes for medical content
   - Returns appropriate responses for refinement requests

3. **Test Mock Responses**:
   - Upload any audio file
   - Mock service returns realistic medical transcription
   - Generate SOAP notes
   - Mock service returns properly structured medical documentation

---

## Success Criteria

You've successfully tested all visit documentation features if:

- ✅ Can upload audio files as doctor
- ✅ Can record audio using microphone
- ✅ Transcription completes successfully with mock service
- ✅ Can generate SOAP notes from transcription
- ✅ All four SOAP sections populate correctly
- ✅ Can manually edit SOAP sections
- ✅ AI refinement works for individual sections
- ✅ Can save SOAP notes to visit record
- ✅ Multiple transcriptions appear in list
- ✅ File validation works (size, type)
- ✅ Error handling works correctly
- ✅ RBAC works (patients can't access Visit Docs)
- ✅ No console errors in browser
- ✅ All text is readable with good contrast

---

## Known Limitations

### Current Phase (Mock Mode):
- ❌ **Real Azure Speech Services** - Not connected yet (using mock)
- ❌ **Real-time Streaming Transcription** - File upload only
- ❌ **Real Azure OpenAI** - Using mock responses
- ❌ **ICD-10 Code Suggestions** - Endpoint implemented but not in UI
- ❌ **Audio Storage in Azure Blob** - Using local/mock storage

### Next Implementation Phase:
1. Connect real Azure Speech Services
2. Implement real-time streaming transcription
3. Connect real Azure OpenAI GPT-4o
4. Add ICD-10 code suggestion UI
5. Implement Azure Blob Storage for audio files
6. Add visit end workflow
7. Add FHIR integration for SOAP notes

---

## Troubleshooting

### Transcription stays in "Processing" state
- **Cause**: Backend API might have errored
- **Fix**: Check backend logs: `docker-compose logs api --tail 50`
- **Fix**: Restart backend: `docker-compose restart api`

### SOAP Notes generation fails
- **Cause**: No transcription available
- **Fix**: Ensure at least one transcription has status "COMPLETED"
- **Fix**: Check visit ID is correct

### Upload fails silently
- **Cause**: Network error or auth token expired
- **Fix**: Check browser console for errors
- **Fix**: Re-login to refresh auth token
- **Fix**: Verify backend is running: `curl http://localhost:8000/health`

### Changes not persisting
- **Cause**: Save button not clicked
- **Fix**: Always click "Save Notes" after editing
- **Fix**: Look for success toast confirmation

---

## Next Steps

After successfully testing these features:

1. ✅ Review CURRENT_FEATURES_TESTING.md for other features
2. ✅ Test PreVisit.ai symptom checker
3. ✅ Test Medical History form
4. ✅ Test Appoint-Ready features (as doctor)
5. ⏭️ Set up E2E testing with Playwright (PROJECT_PROGRESS.md Task 0.4.7)
6. ⏭️ Prepare for Azure deployment (Phase 1)

---

## Feedback & Issues

If you encounter any issues:
1. Check browser console for errors
2. Check backend logs: `docker-compose logs api --tail 100`
3. Verify services are running: `docker-compose ps`
4. Review API documentation: `http://localhost:8000/docs`
5. Check PROJECT_PROGRESS.md for current status

**Happy Testing!** 🎉
