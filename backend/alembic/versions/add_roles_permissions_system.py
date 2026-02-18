"""Add roles and permissions system

Revision ID: a1b2c3d4e5f6
Revises: add_consent_tables
Create Date: 2026-02-05

This migration:
1. Creates the roles table
2. Creates the user_roles table (many-to-many with scope)
3. Creates the support_access_grants table
4. Migrates existing users.role to user_roles
5. Removes the old role column from users
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = 'add_consent_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create roles table
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('scope', sa.String(20), nullable=False),
        sa.Column('permissions', JSONB, nullable=False, server_default='[]'),
        sa.Column('is_system', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.CheckConstraint("scope IN ('platform', 'regional', 'tenant')", name='roles_scope_check'),
    )
    op.create_index('ix_roles_name', 'roles', ['name'])
    op.create_index('ix_roles_scope', 'roles', ['scope'])

    # 2. Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', UUID(as_uuid=False), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scope_type', sa.String(20), nullable=False),
        sa.Column('scope_id', UUID(as_uuid=False), nullable=True),  # NULL for platform scope
        sa.Column('is_primary', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('granted_by', UUID(as_uuid=False), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("scope_type IN ('platform', 'regional', 'tenant')", name='user_roles_scope_type_check'),
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])
    op.create_index('ix_user_roles_scope', 'user_roles', ['scope_type', 'scope_id'])
    op.create_unique_constraint('uq_user_roles_user_role_scope', 'user_roles', ['user_id', 'role_id', 'scope_type', 'scope_id'])

    # 3. Create support_access_grants table
    op.create_table(
        'support_access_grants',
        sa.Column('id', UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=False), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('granted_to_user_id', UUID(as_uuid=False), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('granted_by_user_id', UUID(as_uuid=False), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('access_level', sa.String(20), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_by', UUID(as_uuid=False), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.CheckConstraint("access_level IN ('metadata', 'full')", name='support_access_level_check'),
    )
    op.create_index('ix_support_access_grants_tenant', 'support_access_grants', ['tenant_id'])
    op.create_index('ix_support_access_grants_active', 'support_access_grants', ['granted_to_user_id'],
                    postgresql_where=sa.text('revoked_at IS NULL'))

    # 4. Seed default roles
    op.execute("""
        INSERT INTO roles (id, name, display_name, description, scope, permissions, is_system) VALUES
        -- Platform roles
        (gen_random_uuid(), 'super_admin', 'Super Administrator', 'Full platform access', 'platform',
         '["*"]'::jsonb, true),
        (gen_random_uuid(), 'compliance_officer', 'Compliance Officer', 'Compliance monitoring and audit access', 'platform',
         '["view_audit_logs", "view_consent_records", "generate_compliance_reports", "view_anonymized_data"]'::jsonb, true),
        (gen_random_uuid(), 'regional_admin', 'Regional Administrator', 'Regional operations management', 'regional',
         '["manage_regional_tenants", "view_regional_analytics", "support_access", "manage_regional_users"]'::jsonb, true),
        (gen_random_uuid(), 'support_agent', 'Support Agent', 'Customer support with consent-based access', 'platform',
         '["view_tenant_metadata", "request_support_access", "manage_tickets"]'::jsonb, true),
        (gen_random_uuid(), 'system', 'System Account', 'Automated service account', 'platform',
         '["send_notifications", "process_billing", "run_jobs", "write_analytics"]'::jsonb, true),
        -- Tenant roles
        (gen_random_uuid(), 'tenant_admin', 'Organization Admin', 'Full organization management', 'tenant',
         '["manage_users", "manage_settings", "view_billing", "manage_billing", "manage_invitations", "view_analytics"]'::jsonb, true),
        (gen_random_uuid(), 'provider', 'Healthcare Provider', 'Clinical access for doctors and nurses', 'tenant',
         '["clinical_access", "manage_patients", "transcription", "view_own_analytics", "manage_appointments"]'::jsonb, true),
        (gen_random_uuid(), 'staff', 'Staff', 'Limited clinical and administrative access', 'tenant',
         '["view_patients", "manage_appointments", "basic_clinical"]'::jsonb, true),
        (gen_random_uuid(), 'patient', 'Patient', 'Patient portal access', 'tenant',
         '["view_own_data", "complete_questionnaires", "manage_own_appointments"]'::jsonb, true);
    """)

    # 5. Migrate existing users.role to user_roles
    # Map old roles to new role names
    op.execute("""
        -- Migrate super_admin users
        INSERT INTO user_roles (user_id, role_id, scope_type, scope_id, is_primary, granted_at)
        SELECT u.id, r.id, 'platform', NULL, true, NOW()
        FROM users u
        JOIN roles r ON r.name = 'super_admin'
        WHERE u.role = 'super_admin';

        -- Migrate tenant admin users
        INSERT INTO user_roles (user_id, role_id, scope_type, scope_id, is_primary, granted_at)
        SELECT u.id, r.id, 'tenant', u.tenant_id::uuid, true, NOW()
        FROM users u
        JOIN roles r ON r.name = 'tenant_admin'
        WHERE u.role = 'admin' AND u.tenant_id IS NOT NULL;

        -- Migrate doctor users to provider role
        INSERT INTO user_roles (user_id, role_id, scope_type, scope_id, is_primary, granted_at)
        SELECT u.id, r.id, 'tenant', u.tenant_id::uuid, true, NOW()
        FROM users u
        JOIN roles r ON r.name = 'provider'
        WHERE u.role = 'doctor' AND u.tenant_id IS NOT NULL;

        -- Migrate nurse users to provider role
        INSERT INTO user_roles (user_id, role_id, scope_type, scope_id, is_primary, granted_at)
        SELECT u.id, r.id, 'tenant', u.tenant_id::uuid, true, NOW()
        FROM users u
        JOIN roles r ON r.name = 'provider'
        WHERE u.role = 'nurse' AND u.tenant_id IS NOT NULL;

        -- Migrate staff users
        INSERT INTO user_roles (user_id, role_id, scope_type, scope_id, is_primary, granted_at)
        SELECT u.id, r.id, 'tenant', u.tenant_id::uuid, true, NOW()
        FROM users u
        JOIN roles r ON r.name = 'staff'
        WHERE u.role = 'staff' AND u.tenant_id IS NOT NULL;

        -- Migrate patient users
        INSERT INTO user_roles (user_id, role_id, scope_type, scope_id, is_primary, granted_at)
        SELECT u.id, r.id, 'tenant', u.tenant_id::uuid, true, NOW()
        FROM users u
        JOIN roles r ON r.name = 'patient'
        WHERE u.role = 'patient' AND u.tenant_id IS NOT NULL;
    """)

    # 6. Add metadata and login tracking columns to users
    op.add_column('users', sa.Column('metadata', JSONB, server_default='{}', nullable=False))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('login_count', sa.Integer, server_default='0', nullable=False))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer, server_default='0', nullable=False))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))

    # 7. Keep old role column for now (will be removed in a follow-up migration after verification)
    # This allows rollback if needed
    # We'll rename it to legacy_role to indicate it's deprecated
    op.alter_column('users', 'role', new_column_name='legacy_role')


def downgrade():
    # 1. Rename legacy_role back to role
    op.alter_column('users', 'legacy_role', new_column_name='role')

    # 2. Remove new columns from users
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'login_count')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'metadata')

    # 3. Drop tables in reverse order
    op.drop_table('support_access_grants')
    op.drop_table('user_roles')
    op.drop_table('roles')
