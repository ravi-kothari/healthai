# MedGenie Internationalization Implementation Plan

## Goal
Transform MedGenie into an international platform with region-aware multi-tenancy, starting with India and Canada markets.

> [!IMPORTANT]
> This plan builds on the approved strategy documents:
> - [Internationalization Strategy](file:///Users/ravi/.gemini/antigravity/brain/a0c31e45-e363-430e-810c-0a9916256dd5/internationalization_strategy.md)
> - [Multi-Tenant Architecture](file:///Users/ravi/.gemini/antigravity/brain/a0c31e45-e363-430e-810c-0a9916256dd5/multi_tenant_architecture.md)

---

## Phase 1: Foundation (i18n Infrastructure)

### [MODIFY] Backend: Add Region Support

#### [MODIFY] [models/tenant.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/models/tenant.py)
- Add `Region` model with fields: id, name, default_language, currency, compliance_framework
- Add `region_id` foreign key to `Organization` model

#### [NEW] [middleware/region.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/middleware/region.py)
- Region-aware tenant middleware
- Extract region from JWT claims
- Set database session context

#### [MODIFY] [routers/tenants.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/routers/tenants.py)
- Add CRUD endpoints for regions (super_admin only)
- Update organization endpoints to include region

---

### [NEW] Frontend: i18n Setup

#### [NEW] [i18n/config.ts](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/frontend/i18n/config.ts)
- Configure `next-intl` for internationalization
- Define supported locales: en, hi, fr

#### [NEW] [messages/en.json](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/frontend/messages/en.json)
- English translation strings

#### [NEW] [messages/hi.json](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/frontend/messages/hi.json)
- Hindi translation strings (landing page + patient-facing)

#### [MODIFY] [middleware.ts](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/frontend/middleware.ts)
- Add locale detection and routing

---

## Phase 2: India Market Features

### WhatsApp Integration

#### [NEW] Backend: WhatsApp Service

##### [NEW] [services/whatsapp/client.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/services/whatsapp/client.py)
- Twilio/Meta WhatsApp Business API client
- Send template messages
- Handle incoming webhooks

##### [NEW] [services/whatsapp/handlers.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/services/whatsapp/handlers.py)
- Appointment booking flow
- Pre-visit questionnaire via WhatsApp
- Prescription delivery

##### [NEW] [routers/whatsapp.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/routers/whatsapp.py)
- Webhook endpoint for incoming messages
- Message status callbacks

### Hindi Language Support

#### [MODIFY] AI Services
- Add Hindi transcription using Azure Speech Services
- Configure AI summaries in Hindi
- Bilingual template support

---

## Phase 3: Canada Market Features

### French Language

#### [NEW] [messages/fr-CA.json](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/frontend/messages/fr-CA.json)
- French Canadian translations

### Provincial Integrations

#### [NEW] [services/ehr/oscar.py](file:///Users/ravi/Documents/Antigravity/azure-healthcare-app/backend/src/api/services/ehr/oscar.py)
- Oscar EHR integration (Canadian market)

---

## Database Migrations

### Migration 001: Add Regions
```sql
CREATE TABLE regions (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    default_language VARCHAR(10) DEFAULT 'en',
    default_currency VARCHAR(3) DEFAULT 'USD',
    timezone VARCHAR(50),
    compliance_framework VARCHAR(50),
    is_active BOOLEAN DEFAULT true
);

INSERT INTO regions VALUES 
('us', 'United States', 'en', 'USD', 'America/New_York', 'HIPAA'),
('in', 'India', 'en', 'INR', 'Asia/Kolkata', 'DPDP'),
('ca', 'Canada', 'en', 'CAD', 'America/Toronto', 'PIPEDA');

ALTER TABLE organizations ADD COLUMN region_id VARCHAR(10) REFERENCES regions(id);
UPDATE organizations SET region_id = 'us';
```

---

## Verification Plan

### Automated Tests
- Unit tests for region middleware
- Integration tests for WhatsApp webhook
- i18n rendering tests for each locale

### Manual Verification
- Test Hindi UI on landing page
- Test WhatsApp appointment flow (sandbox)
- Verify French landing page for Canada

---

## Priority Order

1. **Week 1-2**: Database schema + region model
2. **Week 3-4**: i18n framework + Hindi translations
3. **Week 5-6**: WhatsApp integration (India)
4. **Week 7-8**: French translations (Canada)
5. **Week 9+**: Regional EHR integrations
