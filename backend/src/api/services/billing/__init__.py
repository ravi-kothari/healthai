"""
Billing service package.

Provides abstract interface for payment processing with
implementations for different providers (Stripe, Razorpay).
"""

from src.api.services.billing.provider import (
    BillingProvider,
    get_billing_provider,
    get_provider_for_region,
)

__all__ = [
    "BillingProvider",
    "get_billing_provider",
    "get_provider_for_region",
]
