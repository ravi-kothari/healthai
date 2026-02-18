"""
Billing models for multi-region payment processing.

Supports multiple payment providers:
- Stripe (USA, Canada)
- Razorpay (India)

Models:
- Invoice: Payment records
- PaymentMethod: Stored payment methods
- BillingEvent: Webhook and billing event log
- PlanFeatures: Feature limits per subscription plan
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional

from src.api.database import Base
from src.api.models.base import UUIDMixin, TimestampMixin


class PaymentProvider(str, Enum):
    """Supported payment providers by region."""
    STRIPE = "stripe"          # USA, Canada
    RAZORPAY = "razorpay"      # India
    MANUAL = "manual"          # Manual/offline payments


class InvoiceStatus(str, Enum):
    """Invoice status."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethodType(str, Enum):
    """Payment method types."""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"              # India-specific
    NETBANKING = "netbanking"  # India-specific
    WALLET = "wallet"


class Invoice(Base, UUIDMixin, TimestampMixin):
    """
    Invoice/payment record.

    Tracks all payments made by tenants regardless of payment provider.
    """

    __tablename__ = "invoices"

    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default=InvoiceStatus.PENDING.value, nullable=False)

    # Amounts (stored in smallest currency unit, e.g., cents/paise)
    amount = Column(Integer, nullable=False)  # Amount in smallest unit
    currency = Column(String(3), nullable=False)  # ISO 4217 (USD, INR, CAD)
    tax_amount = Column(Integer, default=0, nullable=False)
    total_amount = Column(Integer, nullable=False)

    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # Payment provider
    provider = Column(String(20), nullable=False)  # stripe, razorpay, manual
    provider_invoice_id = Column(String(100), nullable=True)  # External ID
    provider_payment_id = Column(String(100), nullable=True)  # Payment/charge ID

    # Payment details
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_method_id = Column(String(36), ForeignKey("payment_methods.id"), nullable=True)

    # Description
    description = Column(Text, nullable=True)
    line_items = Column(JSONB, default=list, nullable=False)
    """
    Line items structure:
    [
        {
            "description": "Professional Plan - Monthly",
            "quantity": 1,
            "unit_price": 9900,  # $99.00 in cents
            "amount": 9900
        }
    ]
    """

    # Metadata
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    tenant = relationship("Tenant")
    payment_method = relationship("PaymentMethod")

    __table_args__ = (
        Index('ix_invoices_tenant_status', 'tenant_id', 'status'),
        Index('ix_invoices_provider', 'provider', 'provider_invoice_id'),
    )

    def __repr__(self):
        return f"<Invoice(id={self.id}, number={self.invoice_number}, status={self.status})>"

    @property
    def amount_decimal(self) -> Decimal:
        """Get amount as decimal (e.g., dollars)."""
        divisor = 100 if self.currency in ['USD', 'CAD'] else 100  # Adjust for currency
        return Decimal(self.amount) / divisor

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "tenant_id": self.tenant_id,
            "status": self.status,
            "amount": self.amount,
            "currency": self.currency,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
            "provider": self.provider,
            "description": self.description,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PaymentMethod(Base, UUIDMixin, TimestampMixin):
    """
    Stored payment method for a tenant.

    Stores references to payment methods in external providers.
    Actual card/bank details are stored securely by the provider.
    """

    __tablename__ = "payment_methods"

    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Payment method details
    type = Column(String(20), nullable=False)  # card, bank_transfer, upi, etc.
    provider = Column(String(20), nullable=False)  # stripe, razorpay

    # Provider reference
    provider_method_id = Column(String(100), nullable=False)  # External payment method ID

    # Display info (safe to store)
    display_name = Column(String(100), nullable=True)  # "Visa •••• 4242"
    last_four = Column(String(4), nullable=True)  # Last 4 digits of card/account
    brand = Column(String(50), nullable=True)  # Visa, Mastercard, HDFC, etc.
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)

    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index('ix_payment_methods_tenant_default', 'tenant_id', 'is_default'),
    )

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type={self.type}, display={self.display_name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "type": self.type,
            "provider": self.provider,
            "display_name": self.display_name,
            "last_four": self.last_four,
            "brand": self.brand,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "is_default": self.is_default,
            "is_active": self.is_active,
        }


class BillingEvent(Base, UUIDMixin):
    """
    Billing event log for webhooks and internal events.

    Provides audit trail for all billing-related events.
    """

    __tablename__ = "billing_events"

    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True)

    # Event details
    event_type = Column(String(100), nullable=False)  # payment.succeeded, subscription.updated, etc.
    provider = Column(String(20), nullable=False)
    provider_event_id = Column(String(100), nullable=True, unique=True)  # Webhook event ID

    # Related resources
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=True)
    subscription_id = Column(String(100), nullable=True)

    # Event data
    data = Column(JSONB, nullable=False)

    # Processing status
    processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_billing_events_provider_event', 'provider', 'provider_event_id'),
        Index('ix_billing_events_unprocessed', 'processed', postgresql_where='processed = false'),
    )

    def __repr__(self):
        return f"<BillingEvent(id={self.id}, type={self.event_type})>"


# =============================================================================
# Plan Feature Definitions
# =============================================================================

PLAN_FEATURES: Dict[str, Dict[str, Any]] = {
    "trial": {
        "display_name": "Trial",
        "max_users": 3,
        "max_patients": 50,
        "max_storage_gb": 5,
        "features": {
            "ai_assistant": True,
            "transcription": True,
            "careprep": True,
            "contextai": True,
            "fhir_integration": False,
            "custom_branding": False,
            "api_access": False,
            "sso": False,
            "priority_support": False,
        },
        "trial_days": 14,
        "price_monthly": {
            "USD": 0,
            "CAD": 0,
            "INR": 0,
        },
    },
    "starter": {
        "display_name": "Starter",
        "max_users": 5,
        "max_patients": 200,
        "max_storage_gb": 20,
        "features": {
            "ai_assistant": True,
            "transcription": True,
            "careprep": True,
            "contextai": True,
            "fhir_integration": False,
            "custom_branding": False,
            "api_access": False,
            "sso": False,
            "priority_support": False,
        },
        "price_monthly": {
            "USD": 4900,   # $49/month in cents
            "CAD": 6500,   # $65 CAD/month
            "INR": 399900, # ₹3,999/month in paise
        },
    },
    "professional": {
        "display_name": "Professional",
        "max_users": 20,
        "max_patients": 1000,
        "max_storage_gb": 100,
        "features": {
            "ai_assistant": True,
            "transcription": True,
            "careprep": True,
            "contextai": True,
            "fhir_integration": True,
            "custom_branding": True,
            "api_access": True,
            "sso": False,
            "priority_support": True,
        },
        "price_monthly": {
            "USD": 9900,    # $99/month
            "CAD": 12900,   # $129 CAD/month
            "INR": 799900,  # ₹7,999/month
        },
    },
    "enterprise": {
        "display_name": "Enterprise",
        "max_users": -1,  # Unlimited
        "max_patients": -1,  # Unlimited
        "max_storage_gb": -1,  # Unlimited
        "features": {
            "ai_assistant": True,
            "transcription": True,
            "careprep": True,
            "contextai": True,
            "fhir_integration": True,
            "custom_branding": True,
            "api_access": True,
            "sso": True,
            "priority_support": True,
            "dedicated_support": True,
            "on_premise_option": True,
        },
        "price_monthly": {
            "USD": None,  # Custom pricing
            "CAD": None,
            "INR": None,
        },
    },
}


def get_plan_features(plan_name: str) -> Optional[Dict[str, Any]]:
    """Get features for a subscription plan."""
    return PLAN_FEATURES.get(plan_name)


def get_plan_price(plan_name: str, currency: str) -> Optional[int]:
    """Get monthly price for a plan in a specific currency."""
    plan = PLAN_FEATURES.get(plan_name)
    if plan:
        return plan.get("price_monthly", {}).get(currency)
    return None


def is_feature_available(plan_name: str, feature_name: str) -> bool:
    """Check if a feature is available in a plan."""
    plan = PLAN_FEATURES.get(plan_name)
    if plan:
        return plan.get("features", {}).get(feature_name, False)
    return False
