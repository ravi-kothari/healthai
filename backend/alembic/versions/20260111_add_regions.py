"""Add regions table and region_id to tenants for internationalization

Revision ID: 20240111_regions
Revises: 
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260111_regions'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create regions table
    op.create_table(
        'regions',
        sa.Column('id', sa.String(10), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('default_language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('supported_languages', sa.JSON, nullable=False, server_default='["en"]'),
        sa.Column('default_currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('timezone', sa.String(50), nullable=False),
        sa.Column('compliance_framework', sa.String(50), nullable=False),
        sa.Column('data_center_location', sa.String(100), nullable=True),
        sa.Column('primary_channel', sa.String(50), nullable=False, server_default='email'),
        sa.Column('whatsapp_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('sms_enabled', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('settings', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Insert default regions
    op.execute("""
        INSERT INTO regions (id, name, default_language, supported_languages, default_currency, timezone, compliance_framework, data_center_location, primary_channel, whatsapp_enabled, settings)
        VALUES 
        ('us', 'United States', 'en', '["en", "es"]', 'USD', 'America/New_York', 'HIPAA', 'Azure US East', 'email', false, '{"payment_providers": ["stripe"], "ehr_integrations": ["epic", "cerner"]}'),
        ('in', 'India', 'en', '["en", "hi"]', 'INR', 'Asia/Kolkata', 'DPDP', 'Azure India Central', 'whatsapp', true, '{"payment_providers": ["stripe", "upi"], "ehr_integrations": []}'),
        ('ca', 'Canada', 'en', '["en", "fr"]', 'CAD', 'America/Toronto', 'PIPEDA', 'Azure Canada Central', 'email', false, '{"payment_providers": ["stripe"], "ehr_integrations": ["oscar", "telus"]}'),
        ('uk', 'United Kingdom', 'en', '["en"]', 'GBP', 'Europe/London', 'GDPR', 'Azure UK South', 'email', false, '{"payment_providers": ["stripe"], "ehr_integrations": []}'),
        ('ae', 'United Arab Emirates', 'en', '["en", "ar"]', 'AED', 'Asia/Dubai', 'MOH', 'Azure UAE North', 'whatsapp', true, '{"payment_providers": ["stripe"], "ehr_integrations": []}');
    """)
    
    # Add region_id column to tenants table
    op.add_column('tenants', sa.Column('region_id', sa.String(10), nullable=True))
    
    # Set default region for existing tenants
    op.execute("UPDATE tenants SET region_id = 'us' WHERE region_id IS NULL")
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_tenants_region_id',
        'tenants',
        'regions',
        ['region_id'],
        ['id']
    )
    
    # Add index for faster region lookups
    op.create_index('ix_tenants_region_id', 'tenants', ['region_id'])


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_tenants_region_id', table_name='tenants')
    
    # Remove foreign key
    op.drop_constraint('fk_tenants_region_id', 'tenants', type_='foreignkey')
    
    # Remove region_id column
    op.drop_column('tenants', 'region_id')
    
    # Drop regions table
    op.drop_table('regions')
