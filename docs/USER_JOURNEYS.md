# Healthcare AI Platform - User Journeys

**Document Version:** 2.0
**Last Updated:** November 27, 2024
**Owner:** Product Management
**Status:** Active

---

## Table of Contents

1. [Overview](#overview)
2. [User Types & Authentication Model](#user-types--authentication-model)
3. [Provider Journeys](#provider-journeys)
4. [Patient Journeys (Token-Based)](#patient-journeys-token-based)
5. [Acceptance Criteria](#acceptance-criteria)
6. [Testing Strategy](#testing-strategy)

---

## Overview

The Healthcare AI Platform serves two distinct user types with different authentication and access models:

### **Providers (Traditional Auth)**
- Healthcare professionals (doctors, nurses, staff)
- Email/password authentication
- Full platform access with dashboards
- Create and manage patient appointments
- Generate CarePrep links for patients
- Review patient data in ContextAI

### **Patients (Token-Based Access)**
- No signup or login required
- Access via time-limited token links
- Complete CarePrep forms before appointments
- View post-visit summaries
- No persistent accounts or passwords

---

## User Types & Authentication Model

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PROVIDERS                    PATIENTS                       │
│  ┌──────────────┐            ┌──────────────┐              │
│  │   Signup     │            │  No Signup   │              │
│  │   /signup    │            │              │              │
│  └──────┬───────┘            └──────────────┘              │
│         │                                                   │
│  ┌──────▼───────┐            ┌──────────────┐              │
│  │    Login     │            │ Token Link   │              │
│  │   /login     │            │  (via email) │              │
│  └──────┬───────┘            └──────┬───────┘              │
│         │                           │                       │
│  ┌──────▼───────┐            ┌──────▼───────┐              │
│  │  Dashboard   │            │   CarePrep   │              │
│  │  /provider/* │            │ /careprep/   │              │
│  └──────────────┘            │   [token]    │              │
│                              └──────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### **Data Model:**

**Providers:**
- Stored in `users` table
- Has: email, password_hash, role, profile
- Persistent sessions with JWT tokens
- Role-based access control (RBAC)

**Patients:**
- Stored in `patients` table (separate)
- Has: name, email, phone, demographics
- NO password field
- Access via time-limited tokens in `careprep_tokens` table

---

## Provider Journeys

### Journey P1: Provider Signup & Onboarding

**User Story:**
*"As a healthcare provider, I want to create an account so that I can start using the platform to manage my practice and patients."*

**Entry Point:** `/signup`

**Preconditions:** None

#### Step-by-Step Flow:

**1. Access Signup Page**
- Navigate to `https://healthai.com` or `http://localhost:3000`
- Click "Get Started" or "Sign Up"
- Redirected to `/signup`

**2. Complete Registration Form**
Required fields:
- First Name
- Last Name
- Email Address
- Password (with strength requirements)
- Mobile Phone
- Practice Type (dropdown):
  - Solo Practitioner
  - Group Practice
  - Mental Health Clinic
  - Hospital
  - Counseling Center
  - Private Practice
- Agreement checkbox (Terms, Privacy, BAA)

**3. Submit Registration**
- Form validates all fields
- API POST to `/api/auth/register`
- Account created in database
- Email verification sent

**4. Email Verification**
- Provider receives email with verification link
- Clicks link → email confirmed
- Redirected to login or onboarding

**5. Onboarding Flow** (`/onboarding`)
- Step 1: Practice Information
  - Practice name
  - Address
  - Specialization
  - NPI number
- Step 2: Team Setup (optional)
  - Invite colleagues
  - Set up roles
- Step 3: Preferences
  - Appointment types
  - Working hours
  - Notification settings
- Step 4: Complete → Redirect to dashboard

**Success Criteria:**
- ✅ Provider account created
- ✅ Email verified
- ✅ Profile information complete
- ✅ Access to provider dashboard

**Error Scenarios:**
- Email already exists → Prompt to login
- Weak password → Show requirements
- Email verification fails → Resend option
- API error → Show error message, allow retry

---

### Journey P2: Provider Login

**User Story:**
*"As a returning provider, I want to log in to access my dashboard and patient information."*

**Entry Point:** `/login`

#### Step-by-Step Flow:

**1. Access Login Page**
- Navigate to `/login`
- See login form

**2. Enter Credentials**
- Email
- Password
- Optional: "Remember me" checkbox

**3. Submit**
- API POST to `/api/auth/login`
- Receives JWT token
- Token stored in localStorage/cookie

**4. Redirect**
- Based on role:
  - Provider → `/provider/dashboard`
  - Admin → `/admin/dashboard`

**Success Criteria:**
- ✅ Successfully authenticated
- ✅ Token stored
- ✅ Redirected to appropriate dashboard

---

### Journey P3: Create Appointment & Generate CarePrep Link

**User Story:**
*"As a provider, I want to create an appointment for a patient and send them a CarePrep link so they can prepare for the visit."*

**Entry Point:** Provider dashboard → "New Appointment"

**Preconditions:** Provider logged in

#### Step-by-Step Flow:

**1. Access Appointment Creation**
- From `/provider/dashboard`
- Click "New Appointment" or "Schedule Patient"

**2. Patient Selection/Creation**
Option A: Existing patient
- Search by name or email
- Select from list

Option B: New patient
- Enter basic info:
  - First name, last name
  - Email, phone
  - Date of birth
- Patient record created

**3. Appointment Details**
- Date and time
- Appointment type (New patient, Follow-up, Annual, etc.)
- Duration
- Reason for visit (optional)
- Notes (optional)

**4. Generate CarePrep Link**
- System automatically generates unique token
- Creates record in `careprep_tokens` table:
  ```sql
  {
    token: "unique-uuid",
    patient_id: 123,
    appointment_id: 456,
    expires_at: "2024-12-01T10:00:00Z",
    created_at: "2024-11-27T10:00:00Z"
  }
  ```
- Link format: `https://healthai.com/careprep/[token]`

**5. Send CarePrep Link**
Options:
- Email (default)
- SMS
- Copy link manually

Email content:
```
Subject: Prepare for Your Upcoming Appointment

Hi [Patient Name],

You have an upcoming appointment with Dr. [Provider Name] on [Date] at [Time].

Please complete your pre-visit preparation using this link:
https://healthai.com/careprep/abc123xyz

This will help us provide you with the best care possible.

Best regards,
[Practice Name]
```

**6. Confirmation**
- Appointment appears in provider calendar
- CarePrep status: "Pending" (patient hasn't started)
- Provider can resend link if needed

**Success Criteria:**
- ✅ Appointment created
- ✅ CarePrep link generated
- ✅ Link sent to patient
- ✅ Trackable status (Pending/In Progress/Completed)

---

### Journey P4: Review Patient CarePrep Data (ContextAI)

**User Story:**
*"As a provider, I want to review the patient's CarePrep responses before the appointment so I can prepare for the visit."*

**Entry Point:** Provider dashboard → Appointment → "View CarePrep"

**Preconditions:**
- Appointment scheduled
- Patient has submitted CarePrep

#### Step-by-Step Flow:

**1. Access ContextAI**
- From calendar, click on appointment
- Click "View Patient Context" or "CarePrep Summary"
- Opens `/provider/appointments/[id]/context`

**2. ContextAI Dashboard View**
Displays:

**Chief Complaint:**
- Primary symptoms with severity
- Duration, progression
- Associated symptoms

**AI Analysis:**
- Urgency level (Low/Moderate/High)
- Differential diagnoses suggestions
- Red flags/warning signs
- Recommended questions to ask

**Medical History:**
- Current medications
- Allergies
- Chronic conditions
- Recent hospitalizations
- Family history

**Risk Stratification:**
- Risk score calculation
- Care gaps identified
- Preventive care recommendations

**Insurance & Admin:**
- Insurance verification status
- Prior authorizations needed
- Copay amount

**3. Pre-Appointment Preparation**
Provider can:
- Review all patient-submitted data
- Add notes/questions
- Order pre-visit labs if needed
- Flag items to discuss

**Success Criteria:**
- ✅ All CarePrep data visible
- ✅ AI analysis helpful and accurate
- ✅ Risk assessment clear
- ✅ Provider feels prepared for visit

---

### Journey P5: Conduct Visit & Create SOAP Notes

**User Story:**
*"As a provider during a visit, I want to document the encounter and create SOAP notes efficiently."*

**Entry Point:** Provider dashboard → Start Visit

#### Step-by-Step Flow:

**1. Start Visit**
- Click "Start Visit" on appointment
- Opens `/provider/visits/[id]`
- CarePrep data pre-populated

**2. Visit Documentation Interface**
Features:
- **Real-time Transcription:** Audio → text via Azure Speech
- **SOAP Note Editor:** Structured sections
- **Context Panel:** CarePrep data visible on side
- **Quick Actions:** Order labs, prescriptions, referrals

**3. Audio Transcription** (Optional)
- Click "Start Recording"
- Conversation transcribed in real-time
- AI suggests SOAP note sections

**4. SOAP Note Completion**
Sections:
- **Subjective:** Patient's complaint (pre-filled from CarePrep)
- **Objective:** Vitals, exam findings
- **Assessment:** Diagnoses (ICD-10 codes)
- **Plan:** Treatment, medications, follow-up

**5. Orders & Prescriptions**
- E-prescribe medications
- Order labs/imaging
- Create referrals
- Schedule follow-up

**6. Finalize Visit**
- Review SOAP notes
- Sign/lock notes
- Generate visit summary

**Success Criteria:**
- ✅ Complete SOAP notes
- ✅ All orders placed
- ✅ Visit summary generated
- ✅ Patient receives copy

---

### Journey P6: Send Post-Visit Summary to Patient

**User Story:**
*"As a provider after a visit, I want to send the patient a summary so they understand their care plan."*

**Entry Point:** After finalizing visit notes

#### Step-by-Step Flow:

**1. Generate Patient-Friendly Summary**
System creates:
- Plain-language diagnoses
- Medication instructions
- Follow-up instructions
- Warning signs to watch for
- Lab/imaging results (when available)

**2. Create Access Token**
- Generate unique token for visit summary
- Link format: `https://healthai.com/visit-summary/[token]`
- Token expires after 90 days

**3. Send to Patient**
Email:
```
Subject: Your Visit Summary - [Date]

Hi [Patient Name],

Thank you for your visit on [Date]. Your visit summary is ready:

https://healthai.com/visit-summary/xyz789

This includes:
- Visit notes
- Medications prescribed
- Follow-up instructions
- Lab orders (results will be added when available)

Questions? Reply to this email or call us.
```

**4. Patient Access**
- Patient clicks link
- Views summary (no login required)
- Can download PDF
- Can share with family (if permitted)

**Success Criteria:**
- ✅ Summary generated automatically
- ✅ Link sent via email/SMS
- ✅ Patient can access easily
- ✅ Secure token-based access

---

## Patient Journeys (Token-Based)

### Journey PT1: Receive & Access CarePrep Link

**User Story:**
*"As a patient with an upcoming appointment, I want to prepare for my visit by completing the pre-visit questionnaire."*

**Entry Point:** Email/SMS with CarePrep link

**Preconditions:**
- Provider created appointment
- CarePrep link generated and sent

#### Step-by-Step Flow:

**1. Receive CarePrep Link**
- Email or SMS notification
- Click link: `https://healthai.com/careprep/[token]`

**2. Token Validation**
- System validates token:
  - Exists in database
  - Not expired
  - Not already used (or allow multiple submissions)
- If valid → grant access
- If invalid/expired → show error with support contact

**3. CarePrep Landing Page** (`/careprep/[token]`)
Displays:
- Appointment details (date, time, provider)
- Progress indicator (0% complete)
- Sections to complete:
  - ☐ Tell us about your symptoms
  - ☐ Update your medical history
  - ☐ Verify insurance information
  - ☐ Review & submit

**4. Save & Resume**
- Progress auto-saved every 30 seconds
- Can close and return via same link
- Progress persists

**Success Criteria:**
- ✅ Token validated
- ✅ Patient sees appointment info
- ✅ Can start CarePrep
- ✅ Progress saves automatically

**Error Scenarios:**
- Invalid token → "Link not found. Please contact your provider."
- Expired token → "This link has expired. Please request a new one."
- Already completed → Show summary or allow edits

---

### Journey PT2: Complete Symptom Checker

**User Story:**
*"As a patient, I want to describe my symptoms so my provider knows what I'm experiencing."*

**Entry Point:** CarePrep → "Tell us about your symptoms"

#### Step-by-Step Flow:

**1. Symptom Entry** (`/careprep/[token]/symptoms`)
- **Main Symptom:**
  - Description (free text with autocomplete)
  - When did it start? (date picker)
  - Severity (1-10 scale or Mild/Moderate/Severe)
  - Is it getting better/worse/same?

- **Additional Symptoms:**
  - "Add another symptom" button
  - Same fields for each

- **Context Questions:**
  - What makes it better?
  - What makes it worse?
  - Have you tried any treatments?
  - Have you had this before?

**2. AI Analysis (Background)**
- System sends symptoms to Azure OpenAI
- Generates:
  - Urgency assessment
  - Questions to ask provider
  - Related health topics

**3. Emergency Detection**
If severe/emergency symptoms detected:
```
⚠️ WARNING
Your symptoms may require immediate attention.

If you're experiencing:
- Severe chest pain
- Difficulty breathing
- Loss of consciousness

Please call 911 or go to the nearest emergency room.
```

**4. Save & Continue**
- Data saved to database
- Progress: 33% complete
- Next: Medical history

**Success Criteria:**
- ✅ All symptoms captured
- ✅ AI analysis completes
- ✅ Emergency warnings shown if needed
- ✅ Data persists

---

### Journey PT3: Update Medical History

**User Story:**
*"As a patient, I want to provide my current medical information so my provider has accurate records."*

**Entry Point:** CarePrep → "Update your medical history"

#### Step-by-Step Flow:

**1. Current Medications** (`/careprep/[token]/history`)
- List existing medications (if previously entered)
- For each medication:
  - Name (autocomplete from drug database)
  - Dosage (e.g., "10mg")
  - Frequency (e.g., "Once daily")
  - Reason for taking
- "Add medication" button
- "I don't take any medications" option

**2. Allergies**
- Medication allergies
- Food allergies
- Environmental allergies
- For each:
  - Allergen name
  - Type of reaction
  - Severity
- "No known allergies" option

**3. Medical Conditions**
- Chronic conditions (checkboxes + search):
  - Diabetes
  - Hypertension
  - Asthma
  - Heart disease
  - Cancer
  - Depression/Anxiety
  - Other (specify)

**4. Past Medical History**
- Previous surgeries (name, date)
- Hospitalizations (reason, date)
- Serious illnesses

**5. Family History** (Optional)
- Major illnesses in immediate family
- Relevant genetic conditions

**6. Lifestyle** (Optional)
- Smoking status
- Alcohol use
- Exercise frequency
- Occupation

**7. Save & Continue**
- Data saved
- Progress: 66% complete
- Next: Insurance

**Success Criteria:**
- ✅ All current medications listed
- ✅ Allergies documented
- ✅ Medical history updated
- ✅ Can skip optional sections

---

### Journey PT4: Verify Insurance Information

**User Story:**
*"As a patient, I want to verify my insurance so billing is handled correctly."*

**Entry Point:** CarePrep → "Verify insurance"

#### Step-by-Step Flow:

**1. Insurance Information** (`/careprep/[token]/insurance`)
- Insurance provider (dropdown + search)
- Member/Policy ID
- Group number
- Policyholder (if different from patient)

**2. Insurance Card Upload** (Optional)
- Front of card (photo/scan)
- Back of card
- OCR extracts information automatically
- Patient can verify/correct

**3. Additional Information**
- Preferred pharmacy
- Emergency contact:
  - Name
  - Relationship
  - Phone number

**4. Consents & Agreements**
- HIPAA authorization
- Treatment consent
- Privacy notice acknowledgment
- Communication preferences

**5. Review & Submit**
- Summary of all entered information
- Edit any section
- Final submit button

**6. Completion**
- Confirmation message:
  ```
  ✅ Thank you for completing your pre-visit preparation!

  Your provider has been notified and will review your information
  before your appointment on [Date] at [Time].

  See you soon!
  ```
- Progress: 100% complete
- Email confirmation sent

**Success Criteria:**
- ✅ Insurance verified
- ✅ Emergency contact on file
- ✅ All consents obtained
- ✅ CarePrep marked complete
- ✅ Provider notified

---

### Journey PT5: Access Post-Visit Summary

**User Story:**
*"As a patient after my visit, I want to access my visit summary and follow instructions."*

**Entry Point:** Email/SMS with visit summary link

**Preconditions:** Visit completed, notes finalized

#### Step-by-Step Flow:

**1. Receive Notification**
- Email: "Your visit summary is ready"
- Link: `https://healthai.com/visit-summary/[token]`

**2. Access Summary** (`/visit-summary/[token]`)
- Token validation
- Display visit summary

**3. Visit Summary Content**
Sections:
- **Visit Information:**
  - Date, provider, diagnosis
  - Vitals recorded

- **What We Discussed:**
  - Patient-friendly summary
  - Medical terminology explained

- **Your Diagnoses:**
  - Conditions diagnosed (plain language)
  - ICD-10 codes (optional, for insurance)

- **Medications:**
  - New prescriptions
  - Changes to existing meds
  - Instructions for each

- **Orders:**
  - Lab tests ordered
  - Imaging ordered
  - Results will be added when available

- **Follow-Up Instructions:**
  - When to return
  - Warning signs to watch for
  - Self-care recommendations

- **Next Steps:**
  - Schedule follow-up (link)
  - Prescription refill options
  - Message provider with questions

**4. Actions Available**
- Download PDF
- Print summary
- Share with family member (if authorized)
- Request prescription refill
- Schedule follow-up appointment

**Success Criteria:**
- ✅ Summary accessible within 4 hours of visit
- ✅ All information accurate and clear
- ✅ Medical jargon explained
- ✅ Actionable next steps provided

---

## Acceptance Criteria

### Provider Journeys

**P1: Provider Signup**
- [ ] Registration completes in < 5 minutes
- [ ] Email verification works within 2 minutes
- [ ] All form validations work correctly
- [ ] Password requirements enforced
- [ ] Account created in database
- [ ] Onboarding can be skipped and resumed
- [ ] Mobile responsive

**P2: Provider Login**
- [ ] Successful login redirects to dashboard
- [ ] Failed login shows clear error
- [ ] "Remember me" persists session
- [ ] Password reset flow works
- [ ] Session expires after inactivity

**P3: Create Appointment & CarePrep Link**
- [ ] Can search existing patients
- [ ] Can create new patient record
- [ ] Appointment saves to database
- [ ] Unique token generated
- [ ] Email/SMS sent successfully
- [ ] Link opens in browser correctly
- [ ] Provider can track completion status

**P4: Review CarePrep (ContextAI)**
- [ ] All patient data displays correctly
- [ ] AI analysis completes in < 10 seconds
- [ ] Risk scores calculate accurately
- [ ] Care gaps identified correctly
- [ ] Interface is intuitive and fast

**P5: Visit Documentation**
- [ ] Audio transcription works (if enabled)
- [ ] SOAP notes save automatically
- [ ] Can order labs/prescriptions
- [ ] Notes can be signed/locked
- [ ] Visit summary generates correctly

**P6: Post-Visit Summary**
- [ ] Summary generated within 4 hours
- [ ] Token link sent via email/SMS
- [ ] Patient can access without login
- [ ] PDF download works
- [ ] All content accurate

### Patient Journeys (Token-Based)

**PT1: CarePrep Access**
- [ ] Token validates correctly
- [ ] Expired tokens show helpful error
- [ ] Appointment details display
- [ ] Progress indicator accurate
- [ ] Auto-save works (30 second intervals)

**PT2: Symptom Checker**
- [ ] Can add unlimited symptoms
- [ ] Severity scales work properly
- [ ] AI analysis completes successfully
- [ ] Emergency warnings trigger correctly
- [ ] Data persists between sessions

**PT3: Medical History**
- [ ] Medication autocomplete works
- [ ] Can add/edit/remove items
- [ ] Allergy alerts shown prominently
- [ ] Optional fields can be skipped
- [ ] Previous data pre-populates

**PT4: Insurance Verification**
- [ ] OCR extracts card data accurately
- [ ] Can complete without insurance (self-pay)
- [ ] All consents legally valid
- [ ] Required fields enforced
- [ ] Completion confirmation shown

**PT5: Visit Summary Access**
- [ ] Token grants immediate access
- [ ] Medical terms explained clearly
- [ ] Can download PDF
- [ ] Prescription info accurate
- [ ] Follow-up scheduling works

---

## Testing Strategy

### Test Priority Order

**Phase 1: Provider Core Flows** (Week 1)
1. Provider Signup & Onboarding
2. Provider Login
3. Create Appointment & Generate CarePrep Link

**Phase 2: Patient CarePrep Flow** (Week 1-2)
4. Access CarePrep via Token
5. Complete Symptom Checker
6. Complete Medical History
7. Complete Insurance & Submit

**Phase 3: Provider Review & Visit** (Week 2)
8. Review CarePrep in ContextAI
9. Conduct Visit & Create SOAP Notes
10. Send Post-Visit Summary

**Phase 4: Patient Post-Visit** (Week 2)
11. Access Visit Summary
12. Download/Share Summary

### Test Environments

**Local Development:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: PostgreSQL local
- FHIR: http://localhost:8080

**Staging:**
- TBD

**Production:**
- TBD

### Test Data

**Test Providers:**
```
Dr. Sarah Martinez (Provider)
Email: sarah.martinez@test.healthai.com
Password: TestDoc123!
Practice: Group Practice
```

**Test Patients:**
```
Robert Chen (Patient - No login)
Email: robert.chen@test.patient.com
Phone: (555) 123-4567
DOB: 01/15/1956
```

### Success Metrics

**Provider Adoption:**
- 90% of providers complete signup in < 5 minutes
- 95% of providers successfully generate CarePrep links
- 80% of providers review CarePrep data before visits

**Patient Engagement:**
- 70% of patients complete CarePrep
- 60% complete within 24 hours of receiving link
- 90% of completed CarePreps are helpful to providers

**System Performance:**
- Page load time < 2 seconds
- API response time < 500ms
- AI analysis completion < 10 seconds
- 99.9% uptime

---

## Next Steps

1. Complete provider signup testing (Journey P1)
2. Test CarePrep token generation (Journey P3)
3. Test patient CarePrep completion (Journey PT1-PT4)
4. Test ContextAI provider review (Journey P4)
5. Document all bugs and issues
6. Prioritize fixes
7. Retest after fixes

---

**Document Maintenance:**
- Review quarterly
- Update after major feature releases
- Keep acceptance criteria current
- Track test coverage metrics
