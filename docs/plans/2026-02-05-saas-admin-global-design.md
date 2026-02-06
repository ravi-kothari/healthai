# SaaS Admin Platform - Global Launch Design

**Date:** 2026-02-05
**Status:** Approved
**Regions:** US, India, Canada

## Overview

This document outlines the design for a comprehensive SaaS admin platform to manage a global healthcare solution. The platform supports multi-region operations, role-based access control with healthcare compliance, integrated billing (Stripe + Razorpay), and full analytics suite.

### Goals

1. **Self-managed tenants** - Organizations manage their own users with minimal platform intervention
2. **Healthcare compliance** - HIPAA (US), DPDP (India), PIPEDA/PHIPA (Canada) compliant access controls
3. **Multi-region billing** - Stripe for US/Canada, Razorpay for India
4. **Comprehensive analytics** - Revenue, usage, and health metrics with real-time and periodic reporting

### Non-Goals (for this phase)

- Region management UI (using existing 3 regions only)
- Multi-provider billing abstraction layer (Stripe + Razorpay direct integration first)

---

## 1. Role & Permission Architecture

### 1.1 Database Schema

```sql
-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    scope VARCHAR(20) NOT NULL CHECK (scope IN ('platform', 'regional', 'tenant')),
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User role assignments (many-to-many with scope)
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    scope_type VARCHAR(20) NOT NULL CHECK (scope_type IN ('platform', 'regional', 'tenant')),
    scope_id UUID, -- NULL for platform, region_id or tenant_id otherwise
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, role_id, scope_type, scope_id)
);

-- Indexes for performance
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_scope ON user_roles(scope_type, scope_id);

-- Support access grants (consent-based)
CREATE TABLE support_access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    granted_to_user_id UUID NOT NULL REFERENCES users(id),
    granted_by_user_id UUID NOT NULL REFERENCES users(id),
    reason TEXT NOT NULL,
    access_level VARCHAR(20) NOT NULL CHECK (access_level IN ('metadata', 'full')),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (expires_at <= created_at + INTERVAL '48 hours')
);

CREATE INDEX idx_support_access_active ON support_access_grants(granted_to_user_id)
    WHERE revoked_at IS NULL AND expires_at > NOW();
```

### 1.2 Role Definitions

| Role | Scope | Permissions | Description |
|------|-------|-------------|-------------|
| `super_admin` | Platform | `*` | Full platform access |
| `compliance_officer` | Platform/Regional | `view_audit_logs`, `view_consent_records`, `generate_compliance_reports`, `view_anonymized_data` | Compliance monitoring without PHI access |
| `regional_admin` | Regional | `manage_regional_tenants`, `view_regional_analytics`, `support_access`, `manage_regional_users` | Regional operations |
| `support_agent` | Platform | `view_tenant_metadata`, `request_support_access`, `manage_tickets` | Customer support |
| `system` | Platform | `send_notifications`, `process_billing`, `run_jobs`, `write_analytics` | Automated service accounts |
| `tenant_admin` | Tenant | `manage_users`, `manage_settings`, `view_billing`, `manage_invitations` | Organization admin |
| `provider` | Tenant | `clinical_access`, `manage_patients`, `transcription`, `view_own_analytics` | Doctor/Nurse |
| `staff` | Tenant | `view_patients`, `manage_appointments`, `basic_clinical` | Front desk |
| `patient` | Tenant | `view_own_data`, `complete_questionnaires` | Patient portal |

### 1.3 Permission Definitions

```python
# Platform permissions
PLATFORM_PERMISSIONS = [
    "manage_regions",
    "manage_tenants",
    "manage_platform_users",
    "view_all_analytics",
    "manage_billing",
    "view_audit_logs",
    "view_consent_records",
    "generate_compliance_reports",
    "manage_system_settings",
    "impersonate_users",  # Requires active support grant
]

# Regional permissions
REGIONAL_PERMISSIONS = [
    "manage_regional_tenants",
    "view_regional_analytics",
    "manage_regional_users",
    "view_regional_audit_logs",
    "support_access",
]

# Tenant permissions
TENANT_PERMISSIONS = [
    "manage_users",
    "manage_settings",
    "view_billing",
    "manage_billing",
    "manage_invitations",
    "clinical_access",
    "manage_patients",
    "transcription",
    "view_analytics",
    "manage_appointments",
    "manage_templates",
]
```

### 1.4 Support Access Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     SUPPORT ACCESS FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Tenant Admin initiates support request                     │
│     POST /api/tenants/{id}/support-access                      │
│     { reason: "Need help with billing", access_level: "full" } │
│                                                                 │
│  2. System generates time-limited grant (max 48 hours)          │
│     - Notifies support team                                    │
│     - Creates audit log entry                                  │
│                                                                 │
│  3. Support Agent accesses tenant with grant                    │
│     - All actions logged with grant_id                         │
│     - Access automatically expires                             │
│                                                                 │
│  4. Tenant Admin can revoke early if needed                     │
│     DELETE /api/tenants/{id}/support-access                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Billing Integration

### 2.1 Database Schema

```sql
-- Billing accounts (one per tenant)
CREATE TABLE billing_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
    region_id UUID NOT NULL REFERENCES regions(id),
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('stripe', 'razorpay')),
    provider_customer_id VARCHAR(255),
    provider_subscription_id VARCHAR(255),
    billing_email VARCHAR(255) NOT NULL,
    billing_name VARCHAR(255),
    billing_address JSONB,
    tax_id VARCHAR(100),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_billing_accounts_provider ON billing_accounts(provider, provider_customer_id);

-- Payment methods
CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    billing_account_id UUID NOT NULL REFERENCES billing_accounts(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL,
    provider_payment_method_id VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('card', 'upi', 'bank_transfer', 'wallet')),
    last_four VARCHAR(4),
    brand VARCHAR(50),
    expiry_month INTEGER,
    expiry_year INTEGER,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider, provider_payment_method_id)
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    billing_account_id UUID NOT NULL REFERENCES billing_accounts(id),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    provider VARCHAR(20) NOT NULL,
    provider_invoice_id VARCHAR(255),
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'pending', 'paid', 'failed', 'refunded', 'void')),
    subtotal INTEGER NOT NULL, -- in smallest currency unit (cents/paise)
    tax_amount INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    due_date DATE,
    paid_at TIMESTAMP WITH TIME ZONE,
    pdf_url TEXT,
    hosted_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_invoices_tenant ON invoices(tenant_id, created_at DESC);
CREATE INDEX idx_invoices_status ON invoices(status) WHERE status IN ('pending', 'failed');

-- Subscription events (webhook history)
CREATE TABLE subscription_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    provider VARCHAR(20) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    provider_event_id VARCHAR(255) NOT NULL UNIQUE,
    payload JSONB NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_subscription_events_unprocessed ON subscription_events(created_at)
    WHERE processed_at IS NULL;
```

### 2.2 Provider Selection

```python
# backend/src/api/services/billing/provider.py

from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum

class BillingProvider(str, Enum):
    STRIPE = "stripe"
    RAZORPAY = "razorpay"

def get_billing_provider(region_code: str) -> BillingProvider:
    """Determine billing provider based on region."""
    if region_code == "IN":
        return BillingProvider.RAZORPAY
    else:  # US, CA
        return BillingProvider.STRIPE

class BaseBillingService(ABC):
    """Abstract base class for billing providers."""

    @abstractmethod
    async def create_customer(self, tenant_id: str, email: str, name: str) -> str:
        """Create customer in payment provider. Returns provider_customer_id."""
        pass

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        plan: str,
        payment_method_id: Optional[str] = None
    ) -> dict:
        """Create subscription. Returns subscription details."""
        pass

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> dict:
        """Cancel subscription."""
        pass

    @abstractmethod
    async def change_plan(self, subscription_id: str, new_plan: str) -> dict:
        """Upgrade or downgrade subscription."""
        pass

    @abstractmethod
    async def create_checkout_session(self, tenant_id: str, plan: str, success_url: str, cancel_url: str) -> str:
        """Create hosted checkout session. Returns checkout URL."""
        pass

    @abstractmethod
    async def get_invoices(self, customer_id: str, limit: int = 10) -> list:
        """Get customer invoices."""
        pass

    @abstractmethod
    async def process_webhook(self, payload: bytes, signature: str) -> dict:
        """Process and verify webhook. Returns parsed event."""
        pass
```

### 2.3 Stripe Implementation

```python
# backend/src/api/services/billing/stripe_service.py

import stripe
from .provider import BaseBillingService

class StripeService(BaseBillingService):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    async def create_customer(self, tenant_id: str, email: str, name: str) -> str:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"tenant_id": tenant_id}
        )
        return customer.id

    async def create_subscription(self, customer_id: str, plan: str, payment_method_id: str = None) -> dict:
        price_id = self._get_price_id(plan)

        params = {
            "customer": customer_id,
            "items": [{"price": price_id}],
            "payment_behavior": "default_incomplete",
            "expand": ["latest_invoice.payment_intent"],
        }

        if payment_method_id:
            params["default_payment_method"] = payment_method_id

        subscription = stripe.Subscription.create(**params)
        return {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret
        }

    async def process_webhook(self, payload: bytes, signature: str) -> dict:
        event = stripe.Webhook.construct_event(
            payload, signature, self.webhook_secret
        )
        return {
            "id": event.id,
            "type": event.type,
            "data": event.data.object
        }

    def _get_price_id(self, plan: str) -> str:
        price_map = {
            "starter": settings.STRIPE_PRICE_STARTER,
            "professional": settings.STRIPE_PRICE_PROFESSIONAL,
            "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
        }
        return price_map[plan]
```

### 2.4 Razorpay Implementation

```python
# backend/src/api/services/billing/razorpay_service.py

import razorpay
import hmac
import hashlib
from .provider import BaseBillingService

class RazorpayService(BaseBillingService):
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

    async def create_customer(self, tenant_id: str, email: str, name: str) -> str:
        customer = self.client.customer.create({
            "name": name,
            "email": email,
            "notes": {"tenant_id": tenant_id}
        })
        return customer["id"]

    async def create_subscription(self, customer_id: str, plan: str, payment_method_id: str = None) -> dict:
        plan_id = self._get_plan_id(plan)

        subscription = self.client.subscription.create({
            "plan_id": plan_id,
            "customer_id": customer_id,
            "total_count": 120,  # 10 years max
            "customer_notify": 1
        })

        return {
            "id": subscription["id"],
            "status": subscription["status"],
            "short_url": subscription["short_url"],  # Razorpay hosted page
            "current_end": subscription.get("current_end")
        }

    async def process_webhook(self, payload: bytes, signature: str) -> dict:
        # Verify signature
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid webhook signature")

        data = json.loads(payload)
        return {
            "id": data["event"],
            "type": data["event"],
            "data": data["payload"]
        }

    def _get_plan_id(self, plan: str) -> str:
        plan_map = {
            "starter": settings.RAZORPAY_PLAN_STARTER,
            "professional": settings.RAZORPAY_PLAN_PROFESSIONAL,
            "enterprise": settings.RAZORPAY_PLAN_ENTERPRISE,
        }
        return plan_map[plan]
```

### 2.5 API Endpoints

```python
# backend/src/api/routers/billing.py

router = APIRouter(prefix="/api/billing", tags=["Billing"])

# Tenant-facing endpoints
@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription details."""
    pass

@router.post("/subscribe")
async def create_subscription(
    plan: SubscriptionPlan,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Start a new subscription."""
    pass

@router.post("/change-plan")
async def change_plan(
    new_plan: SubscriptionPlan,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Upgrade or downgrade subscription."""
    pass

@router.delete("/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Cancel subscription."""
    pass

@router.get("/invoices")
async def list_invoices(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice history."""
    pass

@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download invoice PDF."""
    pass

# Webhook endpoints (no auth - signature verified)
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks."""
    pass

@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhooks."""
    pass
```

### 2.6 Pricing Plans

| Plan | US (Stripe) | India (Razorpay) | Canada (Stripe) | Limits |
|------|-------------|------------------|-----------------|--------|
| Starter | $49/mo | ₹2,499/mo | $59 CAD/mo | 10 users, 100 patients |
| Professional | $149/mo | ₹7,499/mo | $179 CAD/mo | 50 users, 500 patients |
| Enterprise | Custom | Custom | Custom | Unlimited |

---

## 3. User Management

### 3.1 Database Schema Enhancements

```sql
-- Enhanced users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;

-- Enhanced invitations table
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    target_type VARCHAR(20) NOT NULL CHECK (target_type IN ('platform', 'tenant')),
    target_id UUID, -- tenant_id if target_type='tenant'
    role_id UUID NOT NULL REFERENCES roles(id),
    custom_message TEXT,
    invited_by_user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'expired', 'revoked')),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    accepted_by_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_target CHECK (
        (target_type = 'platform' AND target_id IS NULL) OR
        (target_type = 'tenant' AND target_id IS NOT NULL)
    )
);

CREATE INDEX idx_invitations_email ON invitations(email, status);
CREATE INDEX idx_invitations_token ON invitations(token) WHERE status = 'pending';

-- User sessions for security
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_user ON user_sessions(user_id) WHERE revoked_at IS NULL;
```

### 3.2 API Endpoints

```python
# backend/src/api/routers/admin_users.py

router = APIRouter(prefix="/api/admin/users", tags=["Admin - Users"])

@router.get("/")
async def list_platform_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List all platform users (super_admin only)."""
    pass

@router.post("/")
async def create_platform_user(
    user_data: PlatformUserCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Create a platform user (super_admin, compliance_officer, etc.)."""
    pass

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get user details including roles and activity."""
    pass

@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Update user details."""
    pass

@router.post("/{user_id}/roles")
async def assign_role(
    user_id: str,
    role_assignment: RoleAssignment,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Assign a role to user."""
    pass

@router.delete("/{user_id}/roles/{role_id}")
async def remove_role(
    user_id: str,
    role_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Remove a role from user."""
    pass

@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Suspend a user."""
    pass

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Activate a suspended user."""
    pass

@router.get("/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get user's active sessions."""
    pass

@router.delete("/{user_id}/sessions")
async def revoke_all_sessions(
    user_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Revoke all user sessions (force logout)."""
    pass

# Invitation endpoints
@router.post("/invitations")
async def create_invitation(
    invitation: InvitationCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Send platform user invitation."""
    pass

@router.get("/invitations")
async def list_invitations(
    status: Optional[str] = None,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List all platform invitations."""
    pass

@router.delete("/invitations/{invitation_id}")
async def revoke_invitation(
    invitation_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Revoke an invitation."""
    pass
```

### 3.3 Tenant User Management

```python
# backend/src/api/routers/tenant_users.py

router = APIRouter(prefix="/api/tenants/{tenant_id}/users", tags=["Tenant - Users"])

@router.get("/")
async def list_tenant_users(
    tenant_id: str,
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """List users in tenant."""
    pass

@router.post("/")
async def create_tenant_user(
    tenant_id: str,
    user_data: TenantUserCreate,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Create user in tenant."""
    pass

@router.post("/invite")
async def invite_tenant_user(
    tenant_id: str,
    invitation: TenantInvitationCreate,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Invite user to join tenant."""
    pass

@router.patch("/{user_id}")
async def update_tenant_user(
    tenant_id: str,
    user_id: str,
    user_data: TenantUserUpdate,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Update tenant user."""
    pass

@router.delete("/{user_id}")
async def remove_tenant_user(
    tenant_id: str,
    user_id: str,
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Remove user from tenant."""
    pass
```

---

## 4. Analytics & Reporting

### 4.1 Database Schema

```sql
-- Analytics events (high-volume, partition by month)
CREATE TABLE analytics_events (
    id UUID DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    region_code VARCHAR(10),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE analytics_events_2026_01 PARTITION OF analytics_events
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE analytics_events_2026_02 PARTITION OF analytics_events
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
-- ... continue for each month

CREATE INDEX idx_analytics_events_tenant ON analytics_events(tenant_id, timestamp);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type, timestamp);

-- Daily rollups (aggregated for fast queries)
CREATE TABLE analytics_daily_rollups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    tenant_id UUID REFERENCES tenants(id),
    region_code VARCHAR(10),

    -- User metrics
    active_users INTEGER NOT NULL DEFAULT 0,
    new_users INTEGER NOT NULL DEFAULT 0,

    -- Usage metrics
    api_calls INTEGER NOT NULL DEFAULT 0,
    transcription_minutes DECIMAL(10,2) NOT NULL DEFAULT 0,
    storage_bytes BIGINT NOT NULL DEFAULT 0,

    -- Feature usage
    feature_usage JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(date, tenant_id)
);

CREATE INDEX idx_daily_rollups_date ON analytics_daily_rollups(date DESC);
CREATE INDEX idx_daily_rollups_tenant ON analytics_daily_rollups(tenant_id, date DESC);

-- Revenue events
CREATE TABLE revenue_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'subscription_start', 'subscription_end',
        'upgrade', 'downgrade',
        'payment_success', 'payment_failed',
        'refund', 'churn'
    )),
    mrr_change INTEGER NOT NULL DEFAULT 0, -- in cents
    total_amount INTEGER, -- in cents
    currency VARCHAR(3) NOT NULL,
    from_plan VARCHAR(50),
    to_plan VARCHAR(50),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_revenue_events_tenant ON revenue_events(tenant_id, timestamp DESC);
CREATE INDEX idx_revenue_events_type ON revenue_events(event_type, timestamp DESC);

-- Tenant health scores (computed daily)
CREATE TABLE tenant_health_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    date DATE NOT NULL,

    overall_score INTEGER NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
    usage_score INTEGER NOT NULL CHECK (usage_score BETWEEN 0 AND 100),
    engagement_score INTEGER NOT NULL CHECK (engagement_score BETWEEN 0 AND 100),
    payment_score INTEGER NOT NULL CHECK (payment_score BETWEEN 0 AND 100),
    growth_score INTEGER NOT NULL CHECK (growth_score BETWEEN 0 AND 100),

    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('healthy', 'at_risk', 'critical')),
    risk_factors JSONB DEFAULT '[]',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(tenant_id, date)
);

CREATE INDEX idx_health_scores_risk ON tenant_health_scores(risk_level, date DESC);

-- Scheduled reports
CREATE TABLE scheduled_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN (
        'daily_summary', 'weekly_digest', 'monthly_review',
        'tenant_usage', 'compliance', 'custom'
    )),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    recipients JSONB NOT NULL DEFAULT '[]', -- array of emails
    filters JSONB DEFAULT '{}', -- { region, tenant_id, etc. }
    format VARCHAR(10) NOT NULL DEFAULT 'pdf' CHECK (format IN ('pdf', 'csv', 'both')),
    template_config JSONB DEFAULT '{}',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_sent_at TIMESTAMP WITH TIME ZONE,
    next_send_at TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4.2 Metrics Computation

```python
# backend/src/api/services/analytics/metrics.py

from datetime import datetime, timedelta
from sqlalchemy import func
from decimal import Decimal

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    # Revenue Metrics
    async def get_mrr(self, region_code: str = None) -> int:
        """Get current MRR in cents."""
        query = self.db.query(func.sum(Tenant.mrr_cents)).filter(
            Tenant.subscription_status == 'active'
        )
        if region_code:
            query = query.join(Region).filter(Region.code == region_code)
        return query.scalar() or 0

    async def get_arr(self, region_code: str = None) -> int:
        """Get ARR (MRR * 12)."""
        return await self.get_mrr(region_code) * 12

    async def get_churn_rate(self, period_days: int = 30) -> Decimal:
        """Calculate churn rate for period."""
        start_date = datetime.utcnow() - timedelta(days=period_days)

        start_mrr = await self._get_mrr_at_date(start_date)
        churned_mrr = self.db.query(func.sum(RevenueEvent.mrr_change)).filter(
            RevenueEvent.event_type == 'churn',
            RevenueEvent.timestamp >= start_date
        ).scalar() or 0

        if start_mrr == 0:
            return Decimal(0)
        return Decimal(abs(churned_mrr)) / Decimal(start_mrr) * 100

    async def get_ltv(self) -> int:
        """Calculate average LTV."""
        avg_revenue = self.db.query(func.avg(Tenant.mrr_cents)).filter(
            Tenant.subscription_status == 'active'
        ).scalar() or 0

        churn_rate = await self.get_churn_rate()
        if churn_rate == 0:
            return int(avg_revenue * 36)  # Assume 3 years if no churn
        return int(avg_revenue / (churn_rate / 100))

    # Usage Metrics
    async def get_dau(self, date: datetime = None) -> int:
        """Get Daily Active Users."""
        date = date or datetime.utcnow().date()
        return self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
            func.date(AnalyticsEvent.timestamp) == date
        ).scalar() or 0

    async def get_mau(self, month: datetime = None) -> int:
        """Get Monthly Active Users."""
        month = month or datetime.utcnow()
        start = month.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)

        return self.db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
            AnalyticsEvent.timestamp >= start,
            AnalyticsEvent.timestamp < end
        ).scalar() or 0

    # Health Metrics
    async def compute_tenant_health(self, tenant_id: str) -> dict:
        """Compute health score for a tenant."""
        tenant = self.db.query(Tenant).get(tenant_id)

        # Usage score (30%)
        usage_score = await self._compute_usage_score(tenant_id)

        # Engagement score (30%)
        engagement_score = await self._compute_engagement_score(tenant_id)

        # Payment score (20%)
        payment_score = await self._compute_payment_score(tenant_id)

        # Growth score (20%)
        growth_score = await self._compute_growth_score(tenant_id)

        overall = int(
            usage_score * 0.3 +
            engagement_score * 0.3 +
            payment_score * 0.2 +
            growth_score * 0.2
        )

        risk_level = 'healthy' if overall >= 70 else 'at_risk' if overall >= 40 else 'critical'

        return {
            'overall_score': overall,
            'usage_score': usage_score,
            'engagement_score': engagement_score,
            'payment_score': payment_score,
            'growth_score': growth_score,
            'risk_level': risk_level,
            'risk_factors': await self._identify_risk_factors(tenant_id)
        }
```

### 4.3 API Endpoints

```python
# backend/src/api/routers/analytics.py

router = APIRouter(prefix="/api/admin/analytics", tags=["Analytics"])

@router.get("/overview")
async def get_overview(
    current_user: User = Depends(require_analytics_access),
    db: Session = Depends(get_db)
):
    """Get key metrics overview."""
    metrics = MetricsService(db)
    return {
        "mrr": await metrics.get_mrr(),
        "arr": await metrics.get_arr(),
        "total_tenants": await metrics.get_total_tenants(),
        "active_users": await metrics.get_dau(),
        "churn_rate": await metrics.get_churn_rate(),
    }

@router.get("/revenue")
async def get_revenue_analytics(
    period: str = "30d",
    region: Optional[str] = None,
    current_user: User = Depends(require_analytics_access),
    db: Session = Depends(get_db)
):
    """Get revenue analytics."""
    pass

@router.get("/usage")
async def get_usage_analytics(
    period: str = "30d",
    tenant_id: Optional[str] = None,
    current_user: User = Depends(require_analytics_access),
    db: Session = Depends(get_db)
):
    """Get usage analytics."""
    pass

@router.get("/health")
async def get_health_analytics(
    risk_level: Optional[str] = None,
    current_user: User = Depends(require_analytics_access),
    db: Session = Depends(get_db)
):
    """Get tenant health analytics."""
    pass

@router.get("/trends")
async def get_trends(
    metric: str,
    period: str = "12m",
    granularity: str = "month",
    current_user: User = Depends(require_analytics_access),
    db: Session = Depends(get_db)
):
    """Get time-series trend data."""
    pass

# WebSocket for real-time
@router.websocket("/live")
async def analytics_live(
    websocket: WebSocket,
    current_user: User = Depends(require_analytics_access)
):
    """Real-time analytics stream."""
    await websocket.accept()
    try:
        while True:
            # Push batched events every second
            events = await get_recent_events()
            await websocket.send_json(events)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
```

### 4.4 Report Generation

```python
# backend/src/api/services/reports/generator.py

from weasyprint import HTML
import csv
from io import BytesIO, StringIO

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.metrics = MetricsService(db)

    async def generate_daily_summary(self) -> dict:
        """Generate daily summary report data."""
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        day_before = yesterday - timedelta(days=1)

        return {
            "date": yesterday.isoformat(),
            "metrics": {
                "mrr": await self.metrics.get_mrr(),
                "mrr_change": await self._get_metric_change("mrr", yesterday, day_before),
                "new_signups": await self._count_signups(yesterday),
                "churns": await self._count_churns(yesterday),
                "active_users": await self.metrics.get_dau(yesterday),
            },
            "alerts": await self._get_alerts(yesterday),
            "failed_payments": await self._get_failed_payments(yesterday),
        }

    async def generate_weekly_digest(self) -> dict:
        """Generate weekly digest report data."""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        prev_start = start_date - timedelta(days=7)

        return {
            "period": {"start": start_date, "end": end_date},
            "metrics": {
                "mrr": await self.metrics.get_mrr(),
                "wow_change": await self._get_wow_change(),
                "new_tenants": await self._count_new_tenants(start_date, end_date),
                "churned_tenants": await self._count_churns_period(start_date, end_date),
                "feature_adoption": await self._get_feature_adoption(),
            },
            "top_growing_tenants": await self._get_top_growing(5),
            "at_risk_tenants": await self._get_at_risk_tenants(5),
        }

    async def generate_monthly_review(self) -> dict:
        """Generate monthly business review data."""
        # ... comprehensive monthly report
        pass

    async def render_pdf(self, report_type: str, data: dict) -> bytes:
        """Render report data as PDF."""
        template = self._get_template(report_type)
        html_content = template.render(**data)

        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    async def render_csv(self, data: dict, columns: list) -> str:
        """Render data as CSV."""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
```

### 4.5 Scheduled Report Jobs

```python
# backend/src/api/jobs/reports.py

from celery import Celery
from celery.schedules import crontab

celery = Celery('reports')

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily summary at 7 AM UTC
    sender.add_periodic_task(
        crontab(hour=7, minute=0),
        send_daily_summaries.s(),
    )

    # Weekly digest on Monday 9 AM UTC
    sender.add_periodic_task(
        crontab(hour=9, minute=0, day_of_week=1),
        send_weekly_digests.s(),
    )

    # Monthly review on 1st of month at 9 AM UTC
    sender.add_periodic_task(
        crontab(hour=9, minute=0, day_of_month=1),
        send_monthly_reviews.s(),
    )

@celery.task
def send_daily_summaries():
    """Send daily summary to all configured recipients."""
    reports = get_active_reports(frequency='daily')
    for report in reports:
        generate_and_send_report.delay(report.id)

@celery.task
def send_weekly_digests():
    """Send weekly digest to all configured recipients."""
    reports = get_active_reports(frequency='weekly')
    for report in reports:
        generate_and_send_report.delay(report.id)

@celery.task
def send_monthly_reviews():
    """Send monthly reviews to all configured recipients."""
    reports = get_active_reports(frequency='monthly')
    for report in reports:
        generate_and_send_report.delay(report.id)

@celery.task
def generate_and_send_report(report_id: str):
    """Generate and email a report."""
    report = get_report(report_id)
    generator = ReportGenerator(get_db())

    # Generate data
    data = generator.generate_report(report.report_type, report.filters)

    # Render in requested format(s)
    attachments = []
    if report.format in ('pdf', 'both'):
        pdf = generator.render_pdf(report.report_type, data)
        attachments.append(('report.pdf', pdf, 'application/pdf'))
    if report.format in ('csv', 'both'):
        csv_data = generator.render_csv(data)
        attachments.append(('report.csv', csv_data, 'text/csv'))

    # Send email
    send_email(
        to=report.recipients,
        subject=f"{report.name} - {datetime.utcnow().strftime('%Y-%m-%d')}",
        template='report_email',
        attachments=attachments
    )

    # Update last_sent
    report.last_sent_at = datetime.utcnow()
    report.next_send_at = calculate_next_send(report.frequency)
    db.commit()
```

---

## 5. Frontend Implementation

### 5.1 Admin Pages Structure

```
/admin
├── /analytics
│   ├── page.tsx (Overview dashboard)
│   ├── /revenue/page.tsx
│   ├── /usage/page.tsx
│   ├── /health/page.tsx
│   └── /live/page.tsx (Real-time dashboard)
├── /users
│   ├── page.tsx (Platform users list)
│   ├── /[id]/page.tsx (User detail)
│   └── /invitations/page.tsx
├── /organizations (existing, enhanced)
│   ├── page.tsx
│   └── /[id]/page.tsx (Org detail with users tab)
├── /billing
│   ├── page.tsx (Overview)
│   ├── /failing/page.tsx (Failed payments)
│   └── /invoices/page.tsx
├── /audit/page.tsx (Audit logs)
├── /reports
│   ├── page.tsx (Scheduled reports)
│   └── /create/page.tsx
└── /settings/page.tsx
```

### 5.2 Key Components

```typescript
// components/admin/AnalyticsCard.tsx
interface AnalyticsCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: React.ComponentType;
  trend?: 'up' | 'down' | 'neutral';
}

// components/admin/TenantHealthBadge.tsx
interface TenantHealthBadgeProps {
  score: number;
  riskLevel: 'healthy' | 'at_risk' | 'critical';
}

// components/admin/RevenueChart.tsx
interface RevenueChartProps {
  data: { date: string; mrr: number; arr: number }[];
  period: '7d' | '30d' | '90d' | '12m';
}

// components/admin/UserRoleManager.tsx
interface UserRoleManagerProps {
  userId: string;
  currentRoles: Role[];
  availableRoles: Role[];
  onRoleChange: (roleId: string, action: 'add' | 'remove') => void;
}

// components/admin/ReportScheduler.tsx
interface ReportSchedulerProps {
  reportType: ReportType;
  onSchedule: (config: ReportConfig) => void;
}
```

---

## 6. Implementation Plan

### Phase 1: Foundation (Week 1-2)
1. Database migrations for new tables
2. Role & permission system backend
3. Update auth middleware for new roles
4. Seed roles and permissions

### Phase 2: User Management (Week 2-3)
1. Admin user API endpoints
2. Tenant user API endpoints (connect existing UI)
3. Invitation system
4. Support access grants
5. Frontend: Users page connected to API

### Phase 3: Billing (Week 3-4)
1. Stripe integration
2. Razorpay integration
3. Webhook handlers
4. Billing API endpoints
5. Frontend: Billing pages

### Phase 4: Analytics (Week 4-5)
1. Analytics event tracking
2. Daily rollup jobs
3. Metrics computation service
4. Health score calculation
5. Frontend: Analytics dashboards

### Phase 5: Reporting (Week 5-6)
1. Report generation service
2. PDF/CSV export
3. Scheduled report jobs (Celery)
4. Email delivery
5. Frontend: Reports management

### Phase 6: Polish & Testing (Week 6-7)
1. End-to-end testing
2. Performance optimization
3. Security audit
4. Documentation
5. Deployment

---

## 7. Security Considerations

### 7.1 Data Access Controls
- RLS policies enforced at database level
- All PHI access requires explicit consent or clinical role
- Support access is time-limited and fully audited

### 7.2 Audit Requirements
- All admin actions logged with user, timestamp, and details
- Audit logs immutable (no UPDATE/DELETE)
- Compliance officer has read-only access to anonymized logs

### 7.3 Billing Security
- PCI compliance via Stripe/Razorpay (no card data stored)
- Webhook signatures verified
- Subscription changes require admin role

### 7.4 API Security
- Rate limiting on all endpoints
- JWT with short expiry + refresh tokens
- Role validation on every request

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Admin page load time | < 2 seconds |
| Analytics data freshness | < 5 minutes |
| Report generation time | < 30 seconds |
| Webhook processing time | < 500ms |
| Support access grant time | < 10 seconds |

---

## Appendix A: Environment Variables

```bash
# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PROFESSIONAL=price_...
STRIPE_PRICE_ENTERPRISE=price_...

# Razorpay
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
RAZORPAY_PLAN_STARTER=plan_...
RAZORPAY_PLAN_PROFESSIONAL=plan_...
RAZORPAY_PLAN_ENTERPRISE=plan_...

# Email (for reports)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG...
EMAIL_FROM=reports@medgenie.com

# Celery (for scheduled jobs)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

**Document Version:** 1.0
**Last Updated:** 2026-02-05
**Authors:** AI-assisted design session
