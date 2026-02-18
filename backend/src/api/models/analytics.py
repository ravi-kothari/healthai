"""
Analytics models for platform metrics and reporting.

Supports three scopes:
- Platform: Overall system metrics
- Regional: Metrics per region (US, CA, IN)
- Tenant: Organization-level metrics

Metrics are stored in time-series format for efficient querying.
"""

from sqlalchemy import Column, String, Integer, DateTime, Numeric, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime, date
from typing import Dict, Any, Optional

from src.api.database import Base
from src.api.models.base import UUIDMixin


class MetricScope(str, Enum):
    """Scope for metrics."""
    PLATFORM = "platform"
    REGIONAL = "regional"
    TENANT = "tenant"


class MetricPeriod(str, Enum):
    """Time period for aggregated metrics."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AnalyticsMetric(Base, UUIDMixin):
    """
    Time-series metrics storage.

    Stores individual metric data points with flexible dimensions.
    Used for dashboards and real-time analytics.
    """

    __tablename__ = "analytics_metrics"

    # Scope and ownership
    scope = Column(String(20), nullable=False)  # platform, regional, tenant
    scope_id = Column(String(36), nullable=True)  # region_id or tenant_id

    # Metric identification
    metric_name = Column(String(100), nullable=False)  # e.g., "active_users", "visits_completed"
    metric_category = Column(String(50), nullable=False)  # e.g., "usage", "clinical", "billing"

    # Time dimension
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly

    # Values
    value = Column(Numeric(20, 4), nullable=False)  # Main metric value
    count = Column(Integer, default=1, nullable=False)  # Count for averaging

    # Dimensions (for filtering/grouping)
    dimensions = Column(JSONB, default=dict, nullable=False)
    """
    Dimensions example:
    {
        "plan": "professional",
        "region": "US",
        "user_role": "provider"
    }
    """

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_analytics_metrics_scope', 'scope', 'scope_id'),
        Index('ix_analytics_metrics_name_time', 'metric_name', 'timestamp'),
        Index('ix_analytics_metrics_category', 'metric_category', 'period'),
        # Composite for common queries
        Index('ix_analytics_metrics_lookup', 'scope', 'scope_id', 'metric_name', 'period', 'timestamp'),
    )

    def __repr__(self):
        return f"<AnalyticsMetric(name={self.metric_name}, scope={self.scope}, value={self.value})>"


class AnalyticsSnapshot(Base, UUIDMixin):
    """
    Point-in-time snapshot of key metrics.

    Used for dashboard displays and quick lookups.
    Updated periodically (e.g., every hour).
    """

    __tablename__ = "analytics_snapshots"

    # Scope
    scope = Column(String(20), nullable=False)
    scope_id = Column(String(36), nullable=True)

    # Snapshot time
    snapshot_date = Column(DateTime(timezone=True), nullable=False)

    # Key metrics (denormalized for fast access)
    total_users = Column(Integer, default=0, nullable=False)
    active_users_24h = Column(Integer, default=0, nullable=False)
    active_users_7d = Column(Integer, default=0, nullable=False)
    active_users_30d = Column(Integer, default=0, nullable=False)

    total_patients = Column(Integer, default=0, nullable=False)
    new_patients_24h = Column(Integer, default=0, nullable=False)
    new_patients_7d = Column(Integer, default=0, nullable=False)
    new_patients_30d = Column(Integer, default=0, nullable=False)

    total_visits = Column(Integer, default=0, nullable=False)
    visits_24h = Column(Integer, default=0, nullable=False)
    visits_7d = Column(Integer, default=0, nullable=False)
    visits_30d = Column(Integer, default=0, nullable=False)

    # AI usage
    ai_requests_24h = Column(Integer, default=0, nullable=False)
    transcription_minutes_24h = Column(Integer, default=0, nullable=False)

    # Billing (platform/regional only)
    total_tenants = Column(Integer, default=0, nullable=False)
    active_subscriptions = Column(Integer, default=0, nullable=False)
    mrr = Column(Numeric(12, 2), default=0, nullable=False)  # Monthly Recurring Revenue

    # Extended metrics
    extended_metrics = Column(JSONB, default=dict, nullable=False)
    """
    Extended metrics structure:
    {
        "visits_by_type": {"in_person": 100, "telehealth": 50},
        "users_by_role": {"provider": 10, "staff": 5, "patient": 100},
        "storage_used_gb": 45.5,
        "api_calls_24h": 10000
    }
    """

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_analytics_snapshots_scope_date', 'scope', 'scope_id', 'snapshot_date'),
    )

    def __repr__(self):
        return f"<AnalyticsSnapshot(scope={self.scope}, date={self.snapshot_date})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scope": self.scope,
            "scope_id": self.scope_id,
            "snapshot_date": self.snapshot_date.isoformat() if self.snapshot_date else None,
            "users": {
                "total": self.total_users,
                "active_24h": self.active_users_24h,
                "active_7d": self.active_users_7d,
                "active_30d": self.active_users_30d,
            },
            "patients": {
                "total": self.total_patients,
                "new_24h": self.new_patients_24h,
                "new_7d": self.new_patients_7d,
                "new_30d": self.new_patients_30d,
            },
            "visits": {
                "total": self.total_visits,
                "count_24h": self.visits_24h,
                "count_7d": self.visits_7d,
                "count_30d": self.visits_30d,
            },
            "ai_usage": {
                "requests_24h": self.ai_requests_24h,
                "transcription_minutes_24h": self.transcription_minutes_24h,
            },
            "billing": {
                "total_tenants": self.total_tenants,
                "active_subscriptions": self.active_subscriptions,
                "mrr": float(self.mrr) if self.mrr else 0,
            },
            "extended": self.extended_metrics,
        }


class ScheduledReport(Base, UUIDMixin):
    """
    Scheduled report configuration.

    Defines reports that are generated and sent on a schedule.
    """

    __tablename__ = "scheduled_reports"

    # Report details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # usage, billing, clinical, custom

    # Scope
    scope = Column(String(20), nullable=False)
    scope_id = Column(String(36), nullable=True)

    # Schedule
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly (0=Monday)
    day_of_month = Column(Integer, nullable=True)  # 1-28 for monthly
    hour = Column(Integer, default=8, nullable=False)  # Hour to send (UTC)
    timezone = Column(String(50), default="UTC", nullable=False)

    # Recipients
    recipients = Column(JSONB, default=list, nullable=False)
    """
    Recipients structure:
    [
        {"email": "admin@example.com", "name": "Admin"},
        {"user_id": "uuid", "email": "user@example.com"}
    ]
    """

    # Report configuration
    config = Column(JSONB, default=dict, nullable=False)
    """
    Config structure:
    {
        "metrics": ["active_users", "visits", "revenue"],
        "date_range": "last_30_days",
        "groupBy": "week",
        "includeCharts": true,
        "format": "pdf"
    }
    """

    # Status
    is_active = Column(String(1), default='Y', nullable=False)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)

    # Ownership
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index('ix_scheduled_reports_scope', 'scope', 'scope_id'),
        Index('ix_scheduled_reports_next_run', 'next_run_at', postgresql_where="is_active = 'Y'"),
    )

    def __repr__(self):
        return f"<ScheduledReport(name={self.name}, frequency={self.frequency})>"


class ReportExecution(Base, UUIDMixin):
    """
    Record of report executions.

    Tracks when reports were generated and sent.
    """

    __tablename__ = "report_executions"

    report_id = Column(String(36), nullable=False, index=True)
    report_name = Column(String(100), nullable=False)

    # Execution details
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False)  # running, completed, failed

    # Results
    file_path = Column(String(500), nullable=True)  # Path to generated report
    file_size = Column(Integer, nullable=True)
    recipients_sent = Column(Integer, default=0, nullable=False)

    # Errors
    error_message = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, default=dict, nullable=False)

    __table_args__ = (
        Index('ix_report_executions_report_time', 'report_id', 'started_at'),
    )

    def __repr__(self):
        return f"<ReportExecution(report={self.report_name}, status={self.status})>"


# =============================================================================
# Metric Definitions
# =============================================================================

METRIC_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # Usage metrics
    "active_users": {
        "category": "usage",
        "display_name": "Active Users",
        "description": "Number of users who logged in",
        "unit": "users",
        "aggregation": "sum",
    },
    "logins": {
        "category": "usage",
        "display_name": "Login Count",
        "description": "Number of login events",
        "unit": "count",
        "aggregation": "sum",
    },
    "api_requests": {
        "category": "usage",
        "display_name": "API Requests",
        "description": "Total API requests",
        "unit": "count",
        "aggregation": "sum",
    },

    # Clinical metrics
    "visits_created": {
        "category": "clinical",
        "display_name": "Visits Created",
        "description": "Number of visits created",
        "unit": "visits",
        "aggregation": "sum",
    },
    "visits_completed": {
        "category": "clinical",
        "display_name": "Visits Completed",
        "description": "Number of visits completed",
        "unit": "visits",
        "aggregation": "sum",
    },
    "patients_created": {
        "category": "clinical",
        "display_name": "New Patients",
        "description": "Number of patients created",
        "unit": "patients",
        "aggregation": "sum",
    },
    "transcription_minutes": {
        "category": "clinical",
        "display_name": "Transcription Minutes",
        "description": "Minutes of audio transcribed",
        "unit": "minutes",
        "aggregation": "sum",
    },

    # AI metrics
    "ai_requests": {
        "category": "ai",
        "display_name": "AI Requests",
        "description": "Number of AI assistant requests",
        "unit": "count",
        "aggregation": "sum",
    },
    "careprep_completions": {
        "category": "ai",
        "display_name": "CarePrep Completions",
        "description": "Completed CarePrep questionnaires",
        "unit": "count",
        "aggregation": "sum",
    },

    # Billing metrics (platform/regional)
    "new_subscriptions": {
        "category": "billing",
        "display_name": "New Subscriptions",
        "description": "New subscription signups",
        "unit": "count",
        "aggregation": "sum",
    },
    "churned_subscriptions": {
        "category": "billing",
        "display_name": "Churned Subscriptions",
        "description": "Cancelled subscriptions",
        "unit": "count",
        "aggregation": "sum",
    },
    "revenue": {
        "category": "billing",
        "display_name": "Revenue",
        "description": "Total revenue",
        "unit": "currency",
        "aggregation": "sum",
    },
    "mrr": {
        "category": "billing",
        "display_name": "MRR",
        "description": "Monthly Recurring Revenue",
        "unit": "currency",
        "aggregation": "latest",
    },
}


def get_metric_definition(metric_name: str) -> Optional[Dict[str, Any]]:
    """Get the definition for a metric."""
    return METRIC_DEFINITIONS.get(metric_name)
