# Onboarding Wizard Implementation

## ✅ Overview

Comprehensive 5-step onboarding wizard for new provider sign ups with MediGenie branding and backend API integration.

## 🎯 User Flow

```
User Signs Up → Onboarding Wizard → Provider Dashboard
```

### Detailed Flow:
1. User completes signup at `/signup`
2. Redirect to `/onboarding` (automatically, for first-time users)
3. Complete 5-step wizard
4. Submit to backend API
5. Mark onboarding complete in localStorage
6. Redirect to `/provider/dashboard`

### Returning Users:
- If `localStorage.get('onboarding_complete')` exists → skip to dashboard
- If not → go through onboarding wizard

## 📋 Onboarding Steps

### Step 1: Organization Details
**Purpose**: Collect basic organization information

**Fields**:
- Organization Name * (required)
- Organization Type * (required - multiple choice):
  - Medical Clinic
  - Hospital
  - Private Practice
  - Urgent Care
  - Specialty Center
- NPI Number (optional)
- Tax ID/EIN (optional)
- Phone * (required)
- Email * (required)
- Street Address (optional)
- City (optional)
- State (optional)
- ZIP Code (optional)

**Validation**:
- Required fields must be filled
- Email must be valid format
- Phone must be valid format

---

### Step 2: Team Setup
**Purpose**: Invite team members to the platform

**Features**:
- Add unlimited team member invitations
- Assign roles: Staff, Nurse, Doctor, Admin
- Remove invitations
- Role permissions info box

**Fields** (per invite):
- Email address
- Role (dropdown)

**Role Permissions**:
- **Admin**: Full access to all features and settings
- **Doctor**: Patient care, notes, prescriptions
- **Nurse**: Patient vitals, basic notes, scheduling
- **Staff**: Scheduling, patient check-in

---

### Step 3: Feature Preferences
**Purpose**: Choose which MediGenie features to enable

**Features** (toggleable checkboxes):
1. **MediGenie Ambient**
   - Description: "Real-time AI scribe and clinical decision support"
   - Default: ✅ Enabled

2. **Medical Transcription**
   - Description: "Hands-free voice documentation with medical terminology"
   - Default: ✅ Enabled

3. **MediGenie PreVisit**
   - Description: "Patient questionnaires and appointment preparation"
   - Default: ✅ Enabled

4. **FHIR Integration**
   - Description: "Connect with existing EHR systems via HL7 FHIR"
   - Default: ❌ Disabled

**Additional Settings**:
- Timezone selection (dropdown)
  - Eastern, Central, Mountain, Pacific, Alaska, Hawaii

---

### Step 4: Subscription Plan
**Purpose**: Select billing plan

**Plans**:

#### Starter - $99/month
- Up to 10 users
- Up to 500 patients
- MediGenie Ambient (basic)
- Smart clinical templates
- Email support

#### Professional - $299/month ⭐ Most Popular
- Up to 50 users
- Up to 5,000 patients
- MediGenie Ambient (advanced)
- MediGenie PreVisit
- MediGenie Context
- FHIR integration
- Priority support

#### Enterprise - Custom Pricing
- Unlimited users
- Unlimited patients
- Full MediGenie suite
- Custom integrations
- Dedicated account manager
- 24/7 phone support
- On-premise deployment option

**Additional Fields**:
- Billing Email

**Note**: 14-day free trial, no credit card required initially

---

### Step 5: Complete
**Purpose**: Review and confirm setup

**Display**:
- ✅ Success icon
- Organization name
- Organization type
- Number of pending team invitations
- Selected plan (with "14-day trial" note)

**Actions**:
- "Go to Dashboard" button → `/provider/dashboard`
- Link to quick start guide → `/guides`

## 🔧 Technical Implementation

### Files Modified

**1. Onboarding Page**
- **File**: `frontend/app/onboarding/page.tsx`
- **Changes**:
  - Updated branding to MediGenie
  - Added Sparkles icon
  - Updated product names (MediGenie Ambient, MediGenie PreVisit, etc.)
  - Wired `handleComplete()` to backend API
  - Added `onboarding_complete` localStorage flag

**2. Signup Form**
- **File**: `frontend/components/auth/SignupForm.tsx`
- **Changes**:
  - Check `onboarding_complete` flag after signup
  - Redirect to `/onboarding` for new users
  - Redirect to `/provider/dashboard` for returning users

### Backend API Integration

#### Endpoint: `POST /api/organization/onboarding`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {access_token}"
}
```

**Request Body**:
```json
{
  "organization_name": "Metro Health Clinic",
  "organization_type": "clinic",
  "npi_number": "1234567890",
  "tax_id": "12-3456789",
  "phone": "(555) 123-4567",
  "email": "contact@clinic.com",
  "address": "123 Medical Center Dr",
  "city": "San Francisco",
  "state": "CA",
  "zip_code": "94102",
  "team_invites": [
    { "email": "colleague@clinic.com", "role": "doctor" },
    { "email": "nurse@clinic.com", "role": "nurse" }
  ],
  "preferences": {
    "enable_ai": true,
    "enable_transcription": true,
    "enable_fhir": false,
    "enable_careprep": true,
    "timezone": "America/Los_Angeles"
  },
  "selected_plan": "professional",
  "billing_email": "billing@clinic.com"
}
```

**Response** (Success):
```json
{
  "organization_id": "org_abc123",
  "status": "onboarding_complete",
  "message": "Organization setup successful"
}
```

**Error Handling**:
- If API fails, user still proceeds to dashboard
- `onboarding_complete` flag set regardless
- Errors logged to console

### State Management

**localStorage Keys**:
- `access_token`: JWT access token
- `refresh_token`: JWT refresh token
- `user`: User object JSON
- `onboarding_complete`: Boolean flag ("true" or not present)

**Form State** (React useState):
```typescript
{
  // Organization
  organizationName: string,
  organizationType: string,
  npiNumber: string,
  taxId: string,
  phone: string,
  email: string,
  address: string,
  city: string,
  state: string,
  zipCode: string,

  // Team
  invites: [{ email: string, role: string }],

  // Preferences
  enableAI: boolean,
  enableTranscription: boolean,
  enableFHIR: boolean,
  enableCarePrep: boolean,
  timezone: string,

  // Billing
  selectedPlan: string,
  billingEmail: string
}
```

## 🎨 Design Features

### Progress Indicator
- Visual step tracker at top
- Icons for each step
- Checkmark for completed steps
- Highlight for current step
- Progress line connecting steps

### Responsive Design
- Mobile-first approach
- Grid layouts collapse on mobile
- Buttons stack vertically on small screens
- Touch-friendly interactive elements

### Visual Elements
- MediGenie gradient logo (blue to purple)
- Sparkles icon representing AI "magic"
- Color-coded feature icons
- Emerald green for active/selected states
- Clean white cards with subtle shadows

## ✅ Validation & UX

### Field Validation
- Required fields marked with *
- Real-time validation feedback
- Clear error messages
- Disabled "Continue" until required fields filled (future enhancement)

### User Guidance
- Descriptive placeholders
- Helpful info boxes
- Role permissions explained
- Free trial notice on billing page

### Navigation
- "Back" button on all steps (except first)
- "Continue" button advances to next step
- "Complete Setup" button on billing step
- "Go to Dashboard" button on final step
- Cannot skip steps

## 🚀 Future Enhancements

### Phase 1 (Current): ✅ Complete
- 5-step wizard with all fields
- MediGenie branding
- Backend API integration
- localStorage persistence

### Phase 2 (Future):
- [ ] Real-time validation on all fields
- [ ] Save progress (resume later)
- [ ] Skip onboarding option
- [ ] Backend email verification for team invites
- [ ] Payment processing integration
- [ ] Analytics tracking (step completion rates)

### Phase 3 (Future):
- [ ] Video tutorials embedded in steps
- [ ] Live chat support during onboarding
- [ ] Pre-fill data from EHR integrations
- [ ] Onboarding checklist in dashboard
- [ ] Ability to modify onboarding data later

## 📊 Success Metrics

Track these metrics:
- **Completion Rate**: % of users who complete onboarding
- **Drop-off Points**: Which step do users abandon?
- **Time to Complete**: Average time to finish all steps
- **Feature Adoption**: Which features are most/least enabled?
- **Plan Selection**: Distribution of plan choices

## 🧪 Testing Guide

### Manual Testing Steps:

1. **Sign up as new provider**
   - Go to http://localhost:3000/signup
   - Complete signup form
   - Verify redirect to `/onboarding`

2. **Complete Step 1: Organization**
   - Fill organization name
   - Select organization type
   - Fill contact info
   - Click "Continue"

3. **Complete Step 2: Team**
   - Add 2-3 team members
   - Select different roles
   - Remove one invite
   - Add another
   - Click "Continue"

4. **Complete Step 3: Preferences**
   - Toggle features on/off
   - Select timezone
   - Click "Continue"

5. **Complete Step 4: Billing**
   - Select a plan
   - Enter billing email
   - Click "Complete Setup"

6. **Verify Step 5: Complete**
   - Check summary displays correctly
   - Click "Go to Dashboard"
   - Verify redirect to `/provider/dashboard`

7. **Test Returning User**
   - Logout
   - Login again
   - Verify NO redirect to onboarding
   - Verify direct access to dashboard

### Edge Cases to Test:

- [ ] Back button navigation
- [ ] Refresh page mid-onboarding (state lost - expected)
- [ ] API failure (should still allow dashboard access)
- [ ] No team members invited (should be allowed)
- [ ] All features disabled (should be allowed)
- [ ] Already completed onboarding (should skip)

## 📝 Code Examples

### Check Onboarding Status
```typescript
// In any component
const onboardingComplete = localStorage.getItem('onboarding_complete');

if (!onboardingComplete) {
  router.push('/onboarding');
}
```

### Force Re-onboarding (Admin)
```typescript
// Clear the flag to force user through onboarding again
localStorage.removeItem('onboarding_complete');
```

### Skip Onboarding (Development)
```typescript
// Mark as complete without going through wizard
localStorage.setItem('onboarding_complete', 'true');
```

## 🔐 Security Considerations

- ✅ Requires authentication (access token)
- ✅ API validates user session
- ✅ No sensitive data in localStorage
- ✅ Team invites sent via backend (email verification)
- ✅ Payment info NOT collected in wizard (collected later)
- ⚠️ Currently no CSRF protection (add in production)

## 📚 Related Documentation

- `docs/BRANDING_MEDGENIE.md` - Brand identity used in wizard
- `docs/POST_SIGNUP_FLOW.md` - Signup to onboarding flow
- `docs/SIGNUP_FLOW_STATUS.md` - Overall signup implementation

---

**Created**: 2025-11-28
**Status**: Complete ✅
**Next Steps**: Backend API endpoint implementation
