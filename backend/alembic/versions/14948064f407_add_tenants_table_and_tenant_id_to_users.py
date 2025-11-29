"""add tenants table and tenant_id to users

Revision ID: 14948064f407
Revises: d6e7f8g9h0i1
Create Date: 2025-11-29 19:06:43.612750

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '14948064f407'
down_revision = 'd6e7f8g9h0i1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), server_default='USA', nullable=False),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('npi_number', sa.String(length=20), nullable=True),
        sa.Column('organization_type', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='pending_setup', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('subscription_plan', sa.String(length=50), server_default='trial', nullable=False),
        sa.Column('subscription_status', sa.String(length=50), server_default='trial', nullable=False),
        sa.Column('subscription_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subscription_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
        sa.Column('billing_email', sa.String(length=255), nullable=True),
        sa.Column('max_users', sa.Integer(), server_default='5', nullable=False),
        sa.Column('max_patients', sa.Integer(), server_default='100', nullable=False),
        sa.Column('max_storage_gb', sa.Integer(), server_default='10', nullable=False),
        sa.Column('settings', JSON, server_default='{}', nullable=False),
        sa.Column('data_encryption_key_id', sa.String(length=255), nullable=True),
        sa.Column('last_security_audit', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hipaa_baa_signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('onboarding_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('onboarding_step', sa.String(length=50), server_default='welcome', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)
    op.create_index('ix_tenants_domain', 'tenants', ['domain'], unique=True)
    op.create_index('ix_tenants_stripe_customer_id', 'tenants', ['stripe_customer_id'], unique=True)
    op.create_index('ix_tenants_stripe_subscription_id', 'tenants', ['stripe_subscription_id'], unique=True)
    op.create_index('ix_tenants_status_active', 'tenants', ['status', 'is_active'])
    op.create_index('ix_tenants_subscription', 'tenants', ['subscription_plan', 'subscription_status'])

    # Add tenant_id column to users table
    op.add_column('users', sa.Column('tenant_id', sa.String(length=36), nullable=True))
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_foreign_key('fk_users_tenant_id', 'users', 'tenants', ['tenant_id'], ['id'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=36), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=500), nullable=True),
        sa.Column('old_values', JSON, nullable=True),
        sa.Column('new_values', JSON, nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create indexes for audit_logs
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_tenant_created', 'audit_logs', ['tenant_id', 'created_at'])
    op.create_index('ix_audit_logs_user_action', 'audit_logs', ['user_id', 'action'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])

    # Create tenant_invitations table
    op.create_table(
        'tenant_invitations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='staff', nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_accepted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('invited_by_user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['accepted_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'])
    )

    # Create indexes for tenant_invitations
    op.create_index('ix_tenant_invitations_tenant_id', 'tenant_invitations', ['tenant_id'])
    op.create_index('ix_tenant_invitations_token', 'tenant_invitations', ['token'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tenant_invitations')
    op.drop_table('audit_logs')
    op.drop_column('users', 'tenant_id')
    op.drop_table('tenants')
