# Appointment Sync Strategy (Pre-EHR Integration)

## 📋 Overview

Comprehensive strategy for managing appointments and sending CarePrep questionnaires **before** full EHR integration is implemented.

**Problem**: Providers need to send CarePrep links to patients for upcoming appointments, but we don't have EHR integration yet.

**Solution**: Multi-channel appointment input system with manual, bulk import, and third-party calendar sync options.

---

## 🎯 User Journey - Provider Workflow

### Current State (Without EHR)
```
1. Provider checks their practice management system/calendar
2. Sees upcoming appointments for next week
3. Wants to send CarePrep questionnaires to patients
4. ❌ Problem: Appointments not in MediGenie system yet
```

### Target State (With Our Solution)
```
1. Provider imports appointments into MediGenie (one-time or weekly)
   └─ Option A: Manual entry (1-2 minutes per appointment)
   └─ Option B: CSV bulk import (30 seconds for 50+ appointments)
   └─ Option C: Calendar sync (automatic, coming soon)

2. Provider views Calendar tab in MediGenie
   └─ Sees all upcoming appointments
   └─ CarePrep status shown for each appointment

3. Provider sends CarePrep links
   └─ Individual: Click "Send CarePrep" next to appointment
   └─ Bulk: Select multiple, click "Send to All"
   └─ Automatic: Enable auto-send 48 hours before appointment

4. Provider monitors completion
   └─ Dashboard shows "3/10 CarePrep completed"
   └─ Reminders sent automatically if patient hasn't completed
```

---

## 🔧 Implementation Options

### Option 1: Manual Appointment Entry ⭐ (Implemented)

**Best For**: Small practices, <10 appointments/day

**User Flow**:
1. Click "+ New Appointment" button in Calendar tab
2. Fill in modal form:
   - Patient Name (required)
   - Patient Email (required)
   - Patient Phone (required)
   - Date & Time (required)
   - Duration (default: 30 min)
   - Type (New Patient, Follow-up, etc.)
   - Location (Room 101, Virtual, etc.)
   - Notes (optional)
3. Click "Create & Send CarePrep" or just "Create"

**Advantages**:
- ✅ No technical setup required
- ✅ Works immediately
- ✅ Accurate data entry
- ✅ Can add patient details not in other systems

**Disadvantages**:
- ❌ Time-consuming for high-volume practices
- ❌ Requires manual data entry
- ❌ Risk of typos

**Implementation Status**: ✅ UI ready, backend endpoint needed

---

### Option 2: CSV Bulk Import ⭐⭐⭐ (Recommended for MVP)

**Best For**: Medium to large practices, batch importing

**User Flow**:
1. Export appointments from practice management system
   - Examples: Athenahealth, Epic MyChart, Kareo, DrChrono
   - Format: CSV file
2. Click "Import CSV" button in Calendar tab
3. Upload CSV file (validates format)
4. Review imported appointments (shows preview)
5. Click "Confirm Import"
6. System creates appointments and optionally sends CarePrep links

**CSV Format Requirements**:
```csv
patient_name,patient_email,patient_phone,appointment_date,appointment_time,duration_minutes,type,location,notes
"John Smith","john@example.com","555-1234","2025-12-01","09:00",30,"follow-up","Room 101","Diabetes follow-up"
"Jane Doe","jane@example.com","555-5678","2025-12-01","10:00",60,"new-patient","Room 102","First visit"
```

**Validation Rules**:
- Required fields: patient_name, patient_email, appointment_date, appointment_time
- Email format validation
- Phone format validation (optional but recommended)
- Date/time parsing (supports multiple formats)
- Duplicate detection (same patient + same datetime)

**Error Handling**:
- Invalid rows highlighted in preview
- User can fix errors or skip rows
- Partial imports allowed
- Error report downloadable

**Advantages**:
- ✅ Fast: Import 100+ appointments in seconds
- ✅ Integrates with existing systems (via export)
- ✅ No API integration needed
- ✅ Repeatable weekly workflow

**Disadvantages**:
- ❌ Requires export step from PM system
- ❌ Not real-time (manual trigger)
- ❌ Data can become stale

**Implementation Priority**: **HIGH** (Best ROI for MVP)

---

### Option 3: Google Calendar / Outlook Sync ⭐⭐

**Best For**: Solo providers, small practices using consumer calendars

**User Flow**:
1. Click "Sync Calendar" button
2. Choose provider: Google Calendar or Microsoft Outlook
3. Authorize MediGenie to read calendar
4. Select calendar to sync (e.g., "Dr. Smith - Patient Appointments")
5. Enable auto-sync (every hour or daily)
6. System imports calendar events as appointments
7. Provider maps calendar event fields to appointment fields

**Mapping Example**:
```
Google Calendar Event → MediGenie Appointment
-------------------------------------------
Event Title           → Patient Name (extracted)
Event Description     → Notes
Event Start Time      → Appointment Start
Event Duration        → Duration
Event Location        → Location
Attendee Email        → Patient Email (if invited)
```

**Challenges**:
- ❌ Calendar events may not have structured patient data
- ❌ Need to extract patient name from event title
- ❌ Email may not be in event (unless patient invited)
- ❌ OAuth implementation required

**Advantages**:
- ✅ Automatic sync (set it and forget it)
- ✅ Real-time updates
- ✅ Familiar to providers

**Disadvantages**:
- ❌ Complex implementation
- ❌ May require manual data enrichment
- ❌ Not all providers use these calendars

**Implementation Priority**: **MEDIUM** (Phase 2)

---

### Option 4: Practice Management System API Integration ⭐⭐⭐⭐

**Best For**: Long-term solution, enterprise practices

**Supported Systems** (Future):
- Athenahealth API
- Epic FHIR API
- Cerner FHIR API
- DrChrono API
- Kareo API
- AdvancedMD API

**User Flow**:
1. Admin goes to Settings → Integrations
2. Selects PM system (e.g., "Athenahealth")
3. Enters API credentials
4. Authorizes connection
5. System auto-syncs appointments every hour
6. Zero manual work required

**Advantages**:
- ✅ Fully automated
- ✅ Real-time sync
- ✅ Structured data
- ✅ Bidirectional (can write back)

**Disadvantages**:
- ❌ Complex implementation (months of work)
- ❌ Requires API agreements with vendors
- ❌ May have usage fees
- ❌ Each system has different API

**Implementation Priority**: **FUTURE** (Phase 3+)

---

## 🚀 Recommended MVP Approach

### Phase 1 (Week 1-2): Manual + CSV Import ✅

**Goal**: Enable providers to get appointments into system quickly

**Features**:
1. ✅ Calendar tab in provider navigation
2. ✅ Manual appointment creation form
3. ✅ CSV bulk import with validation
4. ✅ Appointment list view (upcoming)
5. ✅ "Send CarePrep" button for each appointment
6. ✅ Bulk "Send to All" action

**User Flow**:
```
Monday morning:
1. Provider exports next 2 weeks of appointments from practice system (2 min)
2. Uploads CSV to MediGenie (30 sec)
3. Reviews & confirms import (1 min)
4. Clicks "Send CarePrep to All Upcoming" (10 sec)
5. Done! 50 patients get questionnaire links via email/SMS

Total time: ~4 minutes for 50+ appointments
```

**Backend API Endpoints Needed**:
- `POST /api/appointments` - Create single appointment
- `POST /api/appointments/bulk-import` - CSV upload & parse
- `GET /api/appointments?start_date=X&end_date=Y` - List appointments
- `POST /api/appointments/{id}/send-careprep` - Send CarePrep link
- `POST /api/appointments/send-careprep-bulk` - Bulk send

---

### Phase 2 (Week 3-4): Calendar Sync

**Goal**: Reduce manual work with automated sync

**Features**:
1. Google Calendar OAuth integration
2. Outlook Calendar OAuth integration
3. Auto-sync every hour
4. Conflict resolution (update vs. create)
5. Manual refresh button

**User Flow**:
```
One-time setup (5 minutes):
1. Connect Google Calendar
2. Select "Patient Appointments" calendar
3. Enable auto-sync
4. Done!

Ongoing:
- System checks calendar every hour
- New appointments automatically imported
- Provider just sends CarePrep links (no data entry)
```

---

### Phase 3 (Future): EHR/PM API Integration

**Goal**: Fully automated bidirectional sync

**Features**:
1. Direct API integration with major PM systems
2. Real-time appointment sync
3. Patient demographic data sync
4. Bidirectional updates (MediGenie → PM system)
5. Automatic CarePrep sending (48 hours before)

**User Flow**:
```
Zero manual work:
- Appointments auto-sync from EHR
- CarePrep auto-sent 48 hours before
- Completed responses auto-saved to EHR
- Provider just reviews context on appointment day
```

---

## 📊 CSV Import Specification

### Required CSV Format

**Headers** (case-insensitive, flexible order):
```
patient_name, patient_email, appointment_date, appointment_time
```

**Optional Headers**:
```
patient_phone, duration_minutes, type, location, notes, patient_dob, patient_gender
```

### Example CSV File

```csv
patient_name,patient_email,patient_phone,appointment_date,appointment_time,duration_minutes,type,location,notes
"Sarah Johnson","sarah.j@email.com","(555) 123-4567","12/15/2025","9:00 AM",30,"follow-up","Room 101","Diabetes check"
"Michael Chen","mchen@email.com","555-234-5678","12/15/2025","10:30 AM",60,"new-patient","Room 102","First visit - referral from Dr. Smith"
"Emily Davis","emily.davis@email.com","(555) 345-6789","12/16/2025","2:00 PM",45,"telehealth","Virtual","Annual physical - video call"
```

### Date/Time Formats Supported

**Dates**:
- `12/15/2025` (MM/DD/YYYY)
- `2025-12-15` (YYYY-MM-DD)
- `15-Dec-2025` (DD-Mon-YYYY)
- `December 15, 2025` (Month DD, YYYY)

**Times**:
- `9:00 AM` or `9:00AM`
- `09:00` (24-hour)
- `9:00a` or `9a`
- `14:30` (24-hour)

### Validation & Error Handling

**Pre-Import Validation**:
1. ✅ File is valid CSV
2. ✅ Has required headers
3. ✅ At least one row of data
4. ✅ File size < 10MB

**Row-Level Validation**:
1. ✅ Email format (RFC 5322)
2. ✅ Phone format (US/International)
3. ✅ Date/time parsing
4. ✅ Future date (not in past)
5. ⚠️ Duplicate detection (same patient + datetime)

**Import Results**:
```
Import Summary:
✅ 45 appointments imported successfully
⚠️ 3 skipped (duplicates)
❌ 2 failed (invalid email)

View Error Report | Download Failed Rows CSV
```

---

## 🔄 Workflow Automation Ideas

### Auto-Send CarePrep
**Trigger**: 48 hours before appointment
**Action**: Send CarePrep questionnaire link via email/SMS
**User Config**: Enable/disable, customize hours (24h, 48h, 72h)

### Reminder for Incomplete
**Trigger**: 24 hours before appointment, CarePrep not completed
**Action**: Send reminder email/SMS
**User Config**: Enable/disable, customize reminder text

### Daily Digest
**Trigger**: 8:00 AM daily
**Action**: Email provider with summary:
- Appointments today: 8
- CarePrep completed: 5/8
- High-risk patients: 2
- Pending lab results: 3

### Weekly Import Reminder
**Trigger**: Monday 9:00 AM
**Action**: Email reminder to import next week's appointments
**User Config**: Enable/disable, customize day/time

---

## 🎨 UI/UX Design

### Calendar Tab Features

**Top Actions Bar**:
```
[MediGenie Logo] Dashboard | Calendar | Visits | New Visit | Templates    [Dr. Smith] [Logout]
```

**Calendar Page Header**:
```
Calendar                                [Sync Calendar] [Import CSV] [+ New Appointment]
Manage appointments and send CarePrep questionnaires
```

**Info Banner** (dismissible):
```
ℹ️ Appointment Management Options
While we're building EHR integration, you can manage appointments by:
• Manual Entry: Click "+ New Appointment" to add patients
• CSV Import: Upload appointment list from your practice management system
• Calendar Sync: Connect Google Calendar or Outlook (coming soon)
```

**Upcoming Appointments Card** (above calendar):
```
Upcoming Appointments                              [Manage CarePrep]

┌─────────────────────────────────────────────────┐
│ Sarah Johnson                    [Send CarePrep]│
│ Dec 15, 2025 at 9:00 AM                        │
├─────────────────────────────────────────────────┤
│ Michael Chen                     [Send CarePrep]│
│ Dec 15, 2025 at 10:30 AM                       │
└─────────────────────────────────────────────────┘

[Send CarePrep to All (10 appointments)]
```

**Calendar Views**:
- Month view (default)
- Week view
- Day view

**Appointment Card** (in calendar):
```
┌──────────────────┐
│ 9:00 AM - 9:30 AM │
│ Sarah Johnson    │
│ Follow-up        │
│ 📋 CarePrep ✓    │
└──────────────────┘
```

---

## 📱 Mobile Considerations

**Responsive Design**:
- Top nav collapses to hamburger menu
- Calendar switches to day view on mobile
- Import buttons stack vertically
- Appointment cards expand to full width

**Quick Actions** (mobile):
- Swipe left on appointment → "Send CarePrep"
- Swipe right → "View Details"
- Long press → Multi-select mode

---

## 🔐 Data Privacy & Security

### Patient Data Handling

**During CSV Import**:
- ✅ File uploaded via HTTPS
- ✅ Validated server-side
- ✅ Stored in encrypted database
- ✅ File deleted after processing
- ❌ Never stored on client side

**Email/Phone Storage**:
- ✅ Encrypted at rest
- ✅ Masked in UI (show only last 4 digits)
- ✅ Full value shown only to authorized users
- ✅ Audit log for all access

### HIPAA Compliance

**BAA Required**:
- ✅ For calendar sync providers (Google, Microsoft)
- ✅ For SMS providers (Twilio)
- ✅ For email providers (SendGrid)

**Data Retention**:
- Appointments: 7 years (HIPAA requirement)
- CarePrep responses: 7 years
- Audit logs: 7 years

---

## 📈 Success Metrics

### Adoption Metrics
- % of providers who import appointments (Target: >80%)
- Average appointments imported per provider (Target: >20/week)
- % using CSV vs. manual entry (Target: >60% CSV)

### Efficiency Metrics
- Time to import 50 appointments (Target: <5 minutes)
- CarePrep send rate (Target: >70% of appointments)
- CarePrep completion rate (Target: >50%)

### Quality Metrics
- CSV import error rate (Target: <5%)
- Duplicate appointment rate (Target: <2%)
- Invalid email rate (Target: <1%)

---

## 🛠️ Technical Implementation

### Backend API Endpoints

#### 1. Create Appointment
```
POST /api/appointments
Authorization: Bearer {token}

Request Body:
{
  "patient_name": "Sarah Johnson",
  "patient_email": "sarah@example.com",
  "patient_phone": "555-123-4567",
  "appointment_date": "2025-12-15",
  "appointment_time": "09:00",
  "duration_minutes": 30,
  "type": "follow-up",
  "location": "Room 101",
  "notes": "Diabetes check"
}

Response: 201 Created
{
  "id": "apt_abc123",
  "patient_id": "pat_xyz789",
  "status": "scheduled",
  "careprep_status": "not_sent"
}
```

#### 2. Bulk Import (CSV)
```
POST /api/appointments/bulk-import
Authorization: Bearer {token}
Content-Type: multipart/form-data

Request: CSV file upload

Response: 200 OK
{
  "total_rows": 50,
  "imported": 45,
  "skipped": 3,
  "failed": 2,
  "errors": [
    {"row": 12, "error": "Invalid email format"},
    {"row": 28, "error": "Date in the past"}
  ]
}
```

#### 3. Send CarePrep Link
```
POST /api/appointments/{appointment_id}/send-careprep
Authorization: Bearer {token}

Request Body:
{
  "send_via": "email",  // or "sms" or "both"
  "message_template": "default"  // optional custom message
}

Response: 200 OK
{
  "sent": true,
  "careprep_url": "https://medgenie.co/careprep/{token}",
  "sent_at": "2025-11-28T10:30:00Z"
}
```

#### 4. Bulk Send CarePrep
```
POST /api/appointments/send-careprep-bulk
Authorization: Bearer {token}

Request Body:
{
  "appointment_ids": ["apt_1", "apt_2", "apt_3"],
  "send_via": "email"
}

Response: 200 OK
{
  "total": 3,
  "sent": 3,
  "failed": 0
}
```

---

## 🎯 Recommended Next Steps

### Week 1: MVP Implementation
1. ✅ Add Calendar tab to provider navigation
2. ✅ Create provider calendar page UI
3. ⏳ Implement manual appointment creation form
4. ⏳ Build CSV upload & validation
5. ⏳ Backend API endpoints

### Week 2: Testing & Polish
1. ⏳ Test CSV import with real PM system exports
2. ⏳ User testing with 2-3 providers
3. ⏳ Fix bugs and edge cases
4. ⏳ Add helpful tooltips and guides
5. ⏳ Create documentation/video tutorial

### Week 3: Launch
1. ⏳ Deploy to production
2. ⏳ Email announcement to providers
3. ⏳ Onboarding call with early adopters
4. ⏳ Monitor usage and gather feedback
5. ⏳ Iterate based on feedback

---

## 📚 Resources

### CSV Templates
- Download: `/templates/appointment-import-template.csv`
- Example: `/templates/appointment-import-example.csv`

### Video Tutorials
- How to export from Athenahealth (3 min)
- How to import CSV into MediGenie (2 min)
- How to send bulk CarePrep links (1 min)

### Integration Guides
- Google Calendar sync setup (coming soon)
- Outlook Calendar sync setup (coming soon)
- Epic FHIR integration (future)

---

**Status**: ✅ Strategy Complete
**Last Updated**: 2025-11-28
**Owner**: Product Team
