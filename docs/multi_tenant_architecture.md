# MedGenie Multi-Tenant Architecture

## Hierarchical Tenancy Model

MedGenie requires a **three-tier hierarchical multi-tenancy** model:

```
┌─────────────────────────────────────────────────────────────────┐
│                     TIER 1: REGION (Country)                    │
│  Data residency, compliance, language, currency, regulations    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  🇺🇸 USA      │  │  🇮🇳 India    │  │  🇨🇦 Canada   │          │
│  │  HIPAA       │  │  DPDP Act    │  │  PIPEDA      │          │
│  │  USD         │  │  INR         │  │  CAD         │          │
│  │  English     │  │  EN/Hindi    │  │  EN/French   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
├─────────┴─────────────────┴─────────────────┴───────────────────┤
│                 TIER 2: ORGANIZATION (SaaS Tenant)              │
│  Healthcare system, hospital network, practice group            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Apollo Hospitals│  │ Sunnybrook      │                      │
│  │ (India)         │  │ Health (Canada) │                      │
│  │ Org ID: org_123 │  │ Org ID: org_456 │                      │
│  └─────────────────┘  └─────────────────┘                      │
│         │                     │                                 │
├─────────┴─────────────────────┴─────────────────────────────────┤
│                    TIER 3: CLINIC/LOCATION                      │
│  Individual practice, department, branch location               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Mumbai   │ │ Delhi    │ │ Toronto  │ │ Montreal │          │
│  │ Clinic   │ │ Branch   │ │ Main     │ │ Campus   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Architecture Options

### Option A: Database-per-Region (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                    Global Control Plane                      │
│  - User authentication (Auth0/Cognito)                      │
│  - Organization registry                                     │
│  - Region routing                                           │
│  - Feature flags                                            │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   US Database   │  │  India Database │  │ Canada Database │
│   (Azure US)    │  │ (Azure India)   │  │ (Azure Canada)  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ organizations   │  │ organizations   │  │ organizations   │
│ clinics         │  │ clinics         │  │ clinics         │
│ users           │  │ users           │  │ users           │
│ patients        │  │ patients        │  │ patients        │
│ visits          │  │ visits          │  │ visits          │
│ documents       │  │ documents       │  │ documents       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Pros:**
- ✅ Complete data isolation by region (compliance)
- ✅ Data never leaves the country
- ✅ Can tune each DB for regional load patterns
- ✅ Region-specific maintenance windows

**Cons:**
- ❌ More infrastructure to manage
- ❌ Cross-region reporting requires aggregation
- ❌ Higher cost for low-volume regions

---

### Option B: Shared Database with Row-Level Security

```sql
-- Every table includes region and tenant columns
CREATE TABLE patients (
    id UUID PRIMARY KEY,
    region_id VARCHAR(10) NOT NULL,      -- 'us', 'in', 'ca'
    organization_id UUID NOT NULL,
    clinic_id UUID NOT NULL,
    first_name VARCHAR(100),
    ...
    CONSTRAINT fk_org FOREIGN KEY (organization_id) 
        REFERENCES organizations(id)
);

-- Row-Level Security Policy
CREATE POLICY tenant_isolation ON patients
    USING (
        organization_id = current_setting('app.current_org')::UUID
        AND region_id = current_setting('app.current_region')
    );
```

**Pros:**
- ✅ Simpler infrastructure
- ✅ Easy cross-region analytics
- ✅ Lower cost for small deployments

**Cons:**
- ❌ Data residency concerns (single location)
- ❌ Compliance risk for strict regulations
- ❌ Performance at scale

---

## Recommended: Hybrid Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLOBAL CONTROL PLANE                         │
│                    (Single Global Instance)                     │
├─────────────────────────────────────────────────────────────────┤
│  • Identity & Access Management (Auth0)                         │
│  • Organization Registry (which org → which region)             │
│  • Feature Flag Service (LaunchDarkly)                          │
│  • Billing & Subscription Management (Stripe)                   │
│  • Global Analytics (aggregated, anonymized)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   API Gateway     │
                    │  (Routes by org)  │
                    └─────────┬─────────┘
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  REGIONAL STACK │  │  REGIONAL STACK │  │  REGIONAL STACK │
│      (USA)      │  │     (India)     │  │    (Canada)     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • API Services  │  │ • API Services  │  │ • API Services  │
│ • PostgreSQL    │  │ • PostgreSQL    │  │ • PostgreSQL    │
│ • Redis Cache   │  │ • Redis Cache   │  │ • Redis Cache   │
│ • Blob Storage  │  │ • Blob Storage  │  │ • Blob Storage  │
│ • AI Services   │  │ • AI Services   │  │ • AI Services   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Data Model

### Tenant Hierarchy Tables

```sql
-- Regions (managed by platform admin)
CREATE TABLE regions (
    id VARCHAR(10) PRIMARY KEY,        -- 'us', 'in', 'ca'
    name VARCHAR(100) NOT NULL,
    default_language VARCHAR(10),
    default_currency VARCHAR(3),
    timezone VARCHAR(50),
    compliance_framework VARCHAR(50),  -- 'HIPAA', 'DPDP', 'PIPEDA'
    data_center_location VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

-- Organizations (SaaS tenants)
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    region_id VARCHAR(10) NOT NULL REFERENCES regions(id),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE,          -- subdomain: apollo.medgenie.com
    subscription_tier VARCHAR(50),     -- 'starter', 'pro', 'enterprise'
    settings JSONB,                    -- org-specific config
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Clinics/Locations (within organization)
CREATE TABLE clinics (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(200) NOT NULL,
    address JSONB,
    timezone VARCHAR(50),
    settings JSONB,                    -- clinic-specific config
    is_active BOOLEAN DEFAULT true
);

-- Users belong to organization, can access multiple clinics
CREATE TABLE users (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE,
    role VARCHAR(50),
    preferred_language VARCHAR(10),
    clinic_access UUID[],              -- array of clinic IDs
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Request Flow

```
User Request
     │
     ▼
┌─────────────────────────────────────┐
│        Global Load Balancer         │
│   (CloudFlare / Azure Front Door)   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│          API Gateway                │
│  1. Authenticate (JWT)              │
│  2. Extract org_id from token       │
│  3. Lookup region for org           │
│  4. Route to regional endpoint      │
└─────────────────┬───────────────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ US API  │  │ IN API  │  │ CA API  │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  US DB  │  │  IN DB  │  │  CA DB  │
└─────────┘  └─────────┘  └─────────┘
```

---

## Tenant Context in Code

### Middleware (Python/FastAPI)

```python
# middleware/tenant.py

class TenantContext:
    region_id: str
    organization_id: UUID
    clinic_id: Optional[UUID]
    user_id: UUID
    language: str
    timezone: str

async def tenant_middleware(request: Request, call_next):
    # Extract from JWT token
    token = request.headers.get("Authorization")
    claims = decode_jwt(token)
    
    # Build tenant context
    request.state.tenant = TenantContext(
        region_id=claims["region_id"],
        organization_id=UUID(claims["org_id"]),
        clinic_id=UUID(claims.get("clinic_id")) if claims.get("clinic_id") else None,
        user_id=UUID(claims["sub"]),
        language=claims.get("language", "en"),
        timezone=claims.get("timezone", "UTC")
    )
    
    # Set database session variables for RLS
    await db.execute(f"SET app.current_org = '{claims['org_id']}'")
    await db.execute(f"SET app.current_region = '{claims['region_id']}'")
    
    return await call_next(request)
```

### Database Connection Routing

```python
# db/connection.py

REGION_DB_URLS = {
    "us": "postgresql://...:5432/medgenie_us",
    "in": "postgresql://...:5432/medgenie_india",
    "ca": "postgresql://...:5432/medgenie_canada",
}

def get_db_for_region(region_id: str) -> AsyncSession:
    db_url = REGION_DB_URLS[region_id]
    engine = create_async_engine(db_url)
    return AsyncSession(engine)
```

---

## Feature Flags by Region/Tenant

```python
# config/features.py

FEATURE_FLAGS = {
    "whatsapp_integration": {
        "regions": ["in", "br", "ae"],  # WhatsApp markets
        "orgs": ["*"],                  # All orgs in those regions
    },
    "french_language": {
        "regions": ["ca"],
        "orgs": ["*"],
    },
    "hindi_language": {
        "regions": ["in"],
        "orgs": ["*"],
    },
    "upi_payments": {
        "regions": ["in"],
        "orgs": ["*"],
    },
    "fax_integration": {
        "regions": ["ca", "us"],
        "orgs": ["*"],
    },
}

def is_feature_enabled(feature: str, tenant: TenantContext) -> bool:
    flag = FEATURE_FLAGS.get(feature)
    if not flag:
        return False
    
    region_match = tenant.region_id in flag["regions"]
    org_match = "*" in flag["orgs"] or str(tenant.organization_id) in flag["orgs"]
    
    return region_match and org_match
```

---

## URL Structure Options

### Option 1: Regional Subdomains
```
app.medgenie.com         → US (default)
app.medgenie.in          → India
app.medgenie.ca          → Canada
apollo.medgenie.in       → Apollo Hospitals (India)
sunnybrook.medgenie.ca   → Sunnybrook (Canada)
```

### Option 2: Path-based Routing
```
app.medgenie.com/us/apollo/...
app.medgenie.com/in/apollo/...
app.medgenie.com/ca/sunnybrook/...
```

### Recommendation: Regional TLD + Org Subdomain
- Better SEO for regional presence
- Clear data jurisdiction signal to users
- Supports regional compliance requirements

---

## Implementation Priority

### Phase 1: Foundation
- [ ] Add `region_id` to all core tables
- [ ] Implement tenant middleware with region support
- [ ] Create region configuration table
- [ ] Update all queries to include region context

### Phase 2: Regional Infrastructure
- [ ] Set up Azure regions (India, Canada)
- [ ] Configure database replication/deployment
- [ ] Implement API gateway routing
- [ ] Deploy regional API instances

### Phase 3: Feature Isolation
- [ ] Implement feature flag system
- [ ] Add region-specific feature toggles
- [ ] Create regional admin panel

---

## Summary

| Tenancy Level | Purpose | Isolation |
|---------------|---------|-----------|
| **Region** | Compliance, data residency, language | Separate databases |
| **Organization** | SaaS customer, billing, branding | Row-level security |
| **Clinic** | Location, scheduling, local config | Shared within org |
