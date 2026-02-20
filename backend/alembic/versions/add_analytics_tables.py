"""Add analytics and reporting tables.

Revision ID: add_analytics_tables
Revises: add_billing_tables
Create Date: 2025-02-18

Tables:
- analytics_metrics: Time-series metrics storage
- analytics_snapshots: Point-in-time dashboard snapshots
- scheduled_reports: Report configuration
- report_executions: Report execution history
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_analytics_tables'
down_revision = 'add_billing_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Analytics metrics - time series data
    op.create_table(
        'analytics_metrics',
        sa.Column('id', sa.String(36), primary_key=True),

        # Scope and ownership
        sa.Column('scope', sa.String(20), nullable=False),  # platform, regional, tenant
        sa.Column('scope_id', sa.String(36), nullable=True),  # region_id or tenant_id

        # Metric identification
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_category', sa.String(50), nullable=False),

        # Time dimension
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),  # hourly, daily, weekly, monthly

        # Values
        sa.Column('value', sa.Numeric(20, 4), nullable=False),
        sa.Column('count', sa.Integer, default=1, nullable=False),

        # Dimensions for filtering/grouping
        sa.Column('dimensions', postgresql.JSONB, server_default='{}', nullable=False),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index('ix_analytics_metrics_timestamp', 'analytics_metrics', ['timestamp'])
    op.create_index('ix_analytics_metrics_scope', 'analytics_metrics', ['scope', 'scope_id'])
    op.create_index('ix_analytics_metrics_name_time', 'analytics_metrics', ['metric_name', 'timestamp'])
    op.create_index('ix_analytics_metrics_category', 'analytics_metrics', ['metric_category', 'period'])
    op.create_index('ix_analytics_metrics_lookup', 'analytics_metrics',
                    ['scope', 'scope_id', 'metric_name', 'period', 'timestamp'])

    # Analytics snapshots - denormalized dashboard data
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', sa.String(36), primary_key=True),

        # Scope
        sa.Column('scope', sa.String(20), nullable=False),
        sa.Column('scope_id', sa.String(36), nullable=True),

        # Snapshot time
        sa.Column('snapshot_date', sa.DateTime(timezone=True), nullable=False),

        # User metrics
        sa.Column('total_users', sa.Integer, default=0, nullable=False),
        sa.Column('active_users_24h', sa.Integer, default=0, nullable=False),
        sa.Column('active_users_7d', sa.Integer, default=0, nullable=False),
        sa.Column('active_users_30d', sa.Integer, default=0, nullable=False),

        # Patient metrics
        sa.Column('total_patients', sa.Integer, default=0, nullable=False),
        sa.Column('new_patients_24h', sa.Integer, default=0, nullable=False),
        sa.Column('new_patients_7d', sa.Integer, default=0, nullable=False),
        sa.Column('new_patients_30d', sa.Integer, default=0, nullable=False),

        # Visit metrics
        sa.Column('total_visits', sa.Integer, default=0, nullable=False),
        sa.Column('visits_24h', sa.Integer, default=0, nullable=False),
        sa.Column('visits_7d', sa.Integer, default=0, nullable=False),
        sa.Column('visits_30d', sa.Integer, default=0, nullable=False),

        # AI usage
        sa.Column('ai_requests_24h', sa.Integer, default=0, nullable=False),
        sa.Column('transcription_minutes_24h', sa.Integer, default=0, nullable=False),

        # Billing (platform/regional only)
        sa.Column('total_tenants', sa.Integer, default=0, nullable=False),
        sa.Column('active_subscriptions', sa.Integer, default=0, nullable=False),
        sa.Column('mrr', sa.Numeric(12, 2), default=0, nullable=False),

        # Extended metrics
        sa.Column('extended_metrics', postgresql.JSONB, server_default='{}', nullable=False),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index('ix_analytics_snapshots_scope_date', 'analytics_snapshots',
                    ['scope', 'scope_id', 'snapshot_date'])

    # Scheduled reports
    op.create_table(
        'scheduled_reports',
        sa.Column('id', sa.String(36), primary_key=True),

        # Report details
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('report_type', sa.String(50), nullable=False),  # usage, billing, clinical, custom

        # Scope
        sa.Column('scope', sa.String(20), nullable=False),
        sa.Column('scope_id', sa.String(36), nullable=True),

        # Schedule
        sa.Column('frequency', sa.String(20), nullable=False),  # daily, weekly, monthly
        sa.Column('day_of_week', sa.Integer, nullable=True),  # 0-6 for weekly
        sa.Column('day_of_month', sa.Integer, nullable=True),  # 1-28 for monthly
        sa.Column('hour', sa.Integer, default=8, nullable=False),  # Hour to send (UTC)
        sa.Column('timezone', sa.String(50), default='UTC', nullable=False),

        # Recipients
        sa.Column('recipients', postgresql.JSONB, server_default='[]', nullable=False),

        # Report configuration
        sa.Column('config', postgresql.JSONB, server_default='{}', nullable=False),

        # Status
        sa.Column('is_active', sa.String(1), default='Y', nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text, nullable=True),

        # Ownership
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )

    op.create_index('ix_scheduled_reports_scope', 'scheduled_reports', ['scope', 'scope_id'])
    # Partial index for active reports due next
    op.execute("""
        CREATE INDEX ix_scheduled_reports_next_run
        ON scheduled_reports (next_run_at)
        WHERE is_active = 'Y'
    """)

    # Report executions
    op.create_table(
        'report_executions',
        sa.Column('id', sa.String(36), primary_key=True),

        sa.Column('report_id', sa.String(36), nullable=False),
        sa.Column('report_name', sa.String(100), nullable=False),

        # Execution details
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),  # running, completed, failed

        # Results
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('recipients_sent', sa.Integer, default=0, nullable=False),

        # Errors
        sa.Column('error_message', sa.Text, nullable=True),

        # Metadata
        sa.Column('metadata', postgresql.JSONB, server_default='{}', nullable=False),
    )

    op.create_index('ix_report_executions_report_id', 'report_executions', ['report_id'])
    op.create_index('ix_report_executions_report_time', 'report_executions', ['report_id', 'started_at'])


def downgrade():
    op.drop_table('report_executions')
    op.drop_table('scheduled_reports')
    op.drop_table('analytics_snapshots')
    op.drop_table('analytics_metrics')
