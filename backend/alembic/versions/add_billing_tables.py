"""Add billing tables for multi-region payment processing.

Revision ID: add_billing_tables
Revises: add_roles_permissions_system
Create Date: 2025-02-18

Tables:
- invoices: Payment records
- payment_methods: Stored payment methods
- billing_events: Webhook/event log
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_billing_tables'
down_revision = 'a1b2c3d4e5f6'  # add_roles_permissions_system
branch_labels = None
depends_on = None


def upgrade():
    # Payment methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),

        # Payment method details
        sa.Column('type', sa.String(20), nullable=False),  # card, bank_transfer, upi, etc.
        sa.Column('provider', sa.String(20), nullable=False),  # stripe, razorpay

        # Provider reference
        sa.Column('provider_method_id', sa.String(100), nullable=False),

        # Display info
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('last_four', sa.String(4), nullable=True),
        sa.Column('brand', sa.String(50), nullable=True),
        sa.Column('exp_month', sa.Integer, nullable=True),
        sa.Column('exp_year', sa.Integer, nullable=True),

        # Status
        sa.Column('is_default', sa.Boolean, default=False, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),

        # Metadata
        sa.Column('metadata', postgresql.JSONB, server_default='{}', nullable=False),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )

    op.create_index('ix_payment_methods_tenant_id', 'payment_methods', ['tenant_id'])
    op.create_index('ix_payment_methods_tenant_default', 'payment_methods', ['tenant_id', 'is_default'])

    # Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),

        # Invoice details
        sa.Column('invoice_number', sa.String(50), unique=True, nullable=False),
        sa.Column('status', sa.String(20), default='pending', nullable=False),

        # Amounts (smallest currency unit)
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('tax_amount', sa.Integer, default=0, nullable=False),
        sa.Column('total_amount', sa.Integer, nullable=False),

        # Billing period
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),

        # Payment provider
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('provider_invoice_id', sa.String(100), nullable=True),
        sa.Column('provider_payment_id', sa.String(100), nullable=True),

        # Payment details
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_method_id', sa.String(36), sa.ForeignKey('payment_methods.id'), nullable=True),

        # Description
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('line_items', postgresql.JSONB, server_default='[]', nullable=False),

        # Metadata
        sa.Column('metadata', postgresql.JSONB, server_default='{}', nullable=False),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )

    op.create_index('ix_invoices_tenant_id', 'invoices', ['tenant_id'])
    op.create_index('ix_invoices_tenant_status', 'invoices', ['tenant_id', 'status'])
    op.create_index('ix_invoices_provider', 'invoices', ['provider', 'provider_invoice_id'])

    # Billing events table
    op.create_table(
        'billing_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='SET NULL'), nullable=True),

        # Event details
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('provider_event_id', sa.String(100), unique=True, nullable=True),

        # Related resources
        sa.Column('invoice_id', sa.String(36), sa.ForeignKey('invoices.id'), nullable=True),
        sa.Column('subscription_id', sa.String(100), nullable=True),

        # Event data
        sa.Column('data', postgresql.JSONB, nullable=False),

        # Processing status
        sa.Column('processed', sa.Boolean, default=False, nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),

        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index('ix_billing_events_tenant_id', 'billing_events', ['tenant_id'])
    op.create_index('ix_billing_events_provider_event', 'billing_events', ['provider', 'provider_event_id'])
    # Partial index for unprocessed events
    op.execute("""
        CREATE INDEX ix_billing_events_unprocessed
        ON billing_events (processed)
        WHERE processed = false
    """)


def downgrade():
    op.drop_table('billing_events')
    op.drop_table('invoices')
    op.drop_table('payment_methods')
