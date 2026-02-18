"""
Abstract billing provider interface.

Defines the contract that all payment providers must implement.
Allows switching between Stripe (US/CA) and Razorpay (India) seamlessly.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes for Provider Responses
# =============================================================================

@dataclass
class CustomerData:
    """Customer data from payment provider."""
    provider_customer_id: str
    email: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SubscriptionData:
    """Subscription data from payment provider."""
    provider_subscription_id: str
    provider_customer_id: str
    plan_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaymentMethodData:
    """Payment method data from provider."""
    provider_method_id: str
    type: str  # card, bank_transfer, upi, etc.
    display_name: str
    last_four: Optional[str] = None
    brand: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False


@dataclass
class InvoiceData:
    """Invoice data from provider."""
    provider_invoice_id: str
    provider_customer_id: str
    status: str
    amount: int  # In smallest currency unit
    currency: str
    description: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    hosted_invoice_url: Optional[str] = None
    pdf_url: Optional[str] = None


@dataclass
class CheckoutSessionData:
    """Checkout session for payment."""
    session_id: str
    checkout_url: str
    expires_at: datetime


@dataclass
class WebhookEvent:
    """Parsed webhook event."""
    event_id: str
    event_type: str
    data: Dict[str, Any]
    created_at: datetime


# =============================================================================
# Abstract Billing Provider
# =============================================================================

class BillingProvider(ABC):
    """
    Abstract base class for billing providers.

    Implementations:
    - StripeProvider: For US and Canada
    - RazorpayProvider: For India
    - StubProvider: For testing/development
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name (stripe, razorpay, etc.)."""
        pass

    # =========================================================================
    # Customer Management
    # =========================================================================

    @abstractmethod
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CustomerData:
        """
        Create a customer in the payment provider.

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata (e.g., tenant_id)

        Returns:
            CustomerData with provider customer ID
        """
        pass

    @abstractmethod
    async def get_customer(self, provider_customer_id: str) -> Optional[CustomerData]:
        """Get customer by provider ID."""
        pass

    @abstractmethod
    async def update_customer(
        self,
        provider_customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CustomerData:
        """Update customer details."""
        pass

    # =========================================================================
    # Subscription Management
    # =========================================================================

    @abstractmethod
    async def create_subscription(
        self,
        provider_customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionData:
        """
        Create a subscription for a customer.

        Args:
            provider_customer_id: Customer ID from provider
            price_id: Price/plan ID from provider
            trial_days: Optional trial period
            metadata: Additional metadata

        Returns:
            SubscriptionData with subscription details
        """
        pass

    @abstractmethod
    async def get_subscription(self, provider_subscription_id: str) -> Optional[SubscriptionData]:
        """Get subscription by provider ID."""
        pass

    @abstractmethod
    async def update_subscription(
        self,
        provider_subscription_id: str,
        price_id: Optional[str] = None,
        cancel_at_period_end: Optional[bool] = None,
    ) -> SubscriptionData:
        """Update subscription (change plan, cancel at period end, etc.)."""
        pass

    @abstractmethod
    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediately: bool = False,
    ) -> SubscriptionData:
        """
        Cancel a subscription.

        Args:
            provider_subscription_id: Subscription ID
            immediately: If True, cancel now. If False, cancel at period end.

        Returns:
            Updated subscription data
        """
        pass

    # =========================================================================
    # Payment Methods
    # =========================================================================

    @abstractmethod
    async def list_payment_methods(
        self,
        provider_customer_id: str,
    ) -> List[PaymentMethodData]:
        """List payment methods for a customer."""
        pass

    @abstractmethod
    async def attach_payment_method(
        self,
        provider_customer_id: str,
        provider_method_id: str,
        set_default: bool = False,
    ) -> PaymentMethodData:
        """Attach a payment method to a customer."""
        pass

    @abstractmethod
    async def detach_payment_method(
        self,
        provider_method_id: str,
    ) -> bool:
        """Detach/remove a payment method."""
        pass

    @abstractmethod
    async def set_default_payment_method(
        self,
        provider_customer_id: str,
        provider_method_id: str,
    ) -> bool:
        """Set a payment method as default for the customer."""
        pass

    # =========================================================================
    # Invoices
    # =========================================================================

    @abstractmethod
    async def list_invoices(
        self,
        provider_customer_id: str,
        limit: int = 10,
    ) -> List[InvoiceData]:
        """List invoices for a customer."""
        pass

    @abstractmethod
    async def get_invoice(self, provider_invoice_id: str) -> Optional[InvoiceData]:
        """Get invoice by provider ID."""
        pass

    # =========================================================================
    # Checkout
    # =========================================================================

    @abstractmethod
    async def create_checkout_session(
        self,
        provider_customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",  # subscription or payment
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CheckoutSessionData:
        """
        Create a checkout session for payment.

        Args:
            provider_customer_id: Customer ID
            price_id: Price/plan to purchase
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            mode: 'subscription' or 'payment'
            metadata: Additional metadata

        Returns:
            Checkout session with URL for redirect
        """
        pass

    @abstractmethod
    async def create_billing_portal_session(
        self,
        provider_customer_id: str,
        return_url: str,
    ) -> str:
        """
        Create a billing portal session URL.

        Allows customers to manage their subscription and payment methods.

        Returns:
            Portal URL for redirect
        """
        pass

    # =========================================================================
    # Webhooks
    # =========================================================================

    @abstractmethod
    async def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> WebhookEvent:
        """
        Verify and parse a webhook from the provider.

        Args:
            payload: Raw request body
            signature: Webhook signature header

        Returns:
            Parsed webhook event

        Raises:
            ValueError: If signature verification fails
        """
        pass


# =============================================================================
# Stub Provider for Development
# =============================================================================

class StubBillingProvider(BillingProvider):
    """
    Stub billing provider for development and testing.

    Does not make real API calls. Returns mock data.
    """

    @property
    def provider_name(self) -> str:
        return "stub"

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CustomerData:
        import uuid
        return CustomerData(
            provider_customer_id=f"stub_cus_{uuid.uuid4().hex[:16]}",
            email=email,
            name=name,
            metadata=metadata,
        )

    async def get_customer(self, provider_customer_id: str) -> Optional[CustomerData]:
        return CustomerData(
            provider_customer_id=provider_customer_id,
            email="stub@example.com",
            name="Stub Customer",
        )

    async def update_customer(
        self,
        provider_customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CustomerData:
        return CustomerData(
            provider_customer_id=provider_customer_id,
            email=email or "stub@example.com",
            name=name,
            metadata=metadata,
        )

    async def create_subscription(
        self,
        provider_customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionData:
        import uuid
        from datetime import timedelta
        now = datetime.utcnow()
        return SubscriptionData(
            provider_subscription_id=f"stub_sub_{uuid.uuid4().hex[:16]}",
            provider_customer_id=provider_customer_id,
            plan_id=price_id,
            status="active" if not trial_days else "trialing",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            metadata=metadata,
        )

    async def get_subscription(self, provider_subscription_id: str) -> Optional[SubscriptionData]:
        from datetime import timedelta
        now = datetime.utcnow()
        return SubscriptionData(
            provider_subscription_id=provider_subscription_id,
            provider_customer_id="stub_cus_xxx",
            plan_id="stub_price_xxx",
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )

    async def update_subscription(
        self,
        provider_subscription_id: str,
        price_id: Optional[str] = None,
        cancel_at_period_end: Optional[bool] = None,
    ) -> SubscriptionData:
        from datetime import timedelta
        now = datetime.utcnow()
        return SubscriptionData(
            provider_subscription_id=provider_subscription_id,
            provider_customer_id="stub_cus_xxx",
            plan_id=price_id or "stub_price_xxx",
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            cancel_at_period_end=cancel_at_period_end or False,
        )

    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediately: bool = False,
    ) -> SubscriptionData:
        from datetime import timedelta
        now = datetime.utcnow()
        return SubscriptionData(
            provider_subscription_id=provider_subscription_id,
            provider_customer_id="stub_cus_xxx",
            plan_id="stub_price_xxx",
            status="canceled" if immediately else "active",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            cancel_at_period_end=not immediately,
        )

    async def list_payment_methods(
        self,
        provider_customer_id: str,
    ) -> List[PaymentMethodData]:
        return [
            PaymentMethodData(
                provider_method_id="stub_pm_xxx",
                type="card",
                display_name="Visa •••• 4242",
                last_four="4242",
                brand="Visa",
                exp_month=12,
                exp_year=2025,
                is_default=True,
            )
        ]

    async def attach_payment_method(
        self,
        provider_customer_id: str,
        provider_method_id: str,
        set_default: bool = False,
    ) -> PaymentMethodData:
        return PaymentMethodData(
            provider_method_id=provider_method_id,
            type="card",
            display_name="Card •••• 0000",
            is_default=set_default,
        )

    async def detach_payment_method(self, provider_method_id: str) -> bool:
        return True

    async def set_default_payment_method(
        self,
        provider_customer_id: str,
        provider_method_id: str,
    ) -> bool:
        return True

    async def list_invoices(
        self,
        provider_customer_id: str,
        limit: int = 10,
    ) -> List[InvoiceData]:
        return [
            InvoiceData(
                provider_invoice_id="stub_inv_xxx",
                provider_customer_id=provider_customer_id,
                status="paid",
                amount=9900,
                currency="USD",
                description="Professional Plan - Monthly",
                paid_at=datetime.utcnow(),
            )
        ]

    async def get_invoice(self, provider_invoice_id: str) -> Optional[InvoiceData]:
        return InvoiceData(
            provider_invoice_id=provider_invoice_id,
            provider_customer_id="stub_cus_xxx",
            status="paid",
            amount=9900,
            currency="USD",
        )

    async def create_checkout_session(
        self,
        provider_customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CheckoutSessionData:
        import uuid
        from datetime import timedelta
        return CheckoutSessionData(
            session_id=f"stub_cs_{uuid.uuid4().hex[:16]}",
            checkout_url=f"{success_url}?session_id=stub_session",
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

    async def create_billing_portal_session(
        self,
        provider_customer_id: str,
        return_url: str,
    ) -> str:
        return f"{return_url}?portal=stub"

    async def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> WebhookEvent:
        import json
        data = json.loads(payload)
        return WebhookEvent(
            event_id="stub_evt_xxx",
            event_type=data.get("type", "test.event"),
            data=data.get("data", {}),
            created_at=datetime.utcnow(),
        )


# =============================================================================
# Provider Factory
# =============================================================================

# Region to provider mapping
REGION_PROVIDERS = {
    "IN": "razorpay",  # India
    "US": "stripe",    # USA
    "CA": "stripe",    # Canada
}

# Provider instances cache
_providers: Dict[str, BillingProvider] = {}


def get_billing_provider(provider_name: str) -> BillingProvider:
    """
    Get a billing provider instance by name.

    Args:
        provider_name: Provider name (stripe, razorpay, stub)

    Returns:
        BillingProvider instance

    Raises:
        ValueError: If provider not supported
    """
    if provider_name in _providers:
        return _providers[provider_name]

    if provider_name == "stub":
        provider = StubBillingProvider()
    elif provider_name == "stripe":
        # TODO: Implement StripeProvider
        logger.warning("Stripe provider not implemented, using stub")
        provider = StubBillingProvider()
    elif provider_name == "razorpay":
        # TODO: Implement RazorpayProvider
        logger.warning("Razorpay provider not implemented, using stub")
        provider = StubBillingProvider()
    else:
        raise ValueError(f"Unknown billing provider: {provider_name}")

    _providers[provider_name] = provider
    return provider


def get_provider_for_region(region_code: str) -> BillingProvider:
    """
    Get the appropriate billing provider for a region.

    Args:
        region_code: ISO country code (US, CA, IN)

    Returns:
        BillingProvider for that region
    """
    provider_name = REGION_PROVIDERS.get(region_code.upper(), "stripe")
    return get_billing_provider(provider_name)
