"""
Analytics service for tracking and querying metrics.

Provides:
- Metric tracking (increment, set, record)
- Dashboard data retrieval
- Time-series queries
- Snapshot generation
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging

from src.api.models.analytics import (
    AnalyticsMetric, AnalyticsSnapshot,
    MetricScope, MetricPeriod, METRIC_DEFINITIONS
)
from src.api.models.user import User
from src.api.models.patient import Patient
from src.api.models.visit import Visit
from src.api.models.tenant import Tenant

logger = logging.getLogger(__name__)


# =============================================================================
# Metric Tracking
# =============================================================================

def track_metric(
    db: Session,
    metric_name: str,
    value: float,
    scope: str = MetricScope.TENANT,
    scope_id: Optional[str] = None,
    dimensions: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
    period: str = MetricPeriod.HOURLY,
) -> AnalyticsMetric:
    """
    Track a metric value.

    Args:
        db: Database session
        metric_name: Name of the metric
        value: Metric value
        scope: platform, regional, or tenant
        scope_id: Region or tenant ID
        dimensions: Additional dimensions for filtering
        timestamp: When the metric occurred (defaults to now)
        period: Aggregation period

    Returns:
        Created AnalyticsMetric
    """
    definition = METRIC_DEFINITIONS.get(metric_name, {})
    category = definition.get("category", "custom")

    metric = AnalyticsMetric(
        scope=scope,
        scope_id=scope_id,
        metric_name=metric_name,
        metric_category=category,
        timestamp=timestamp or datetime.now(timezone.utc),
        period=period,
        value=Decimal(str(value)),
        count=1,
        dimensions=dimensions or {},
    )

    db.add(metric)
    return metric


def increment_metric(
    db: Session,
    metric_name: str,
    scope: str = MetricScope.TENANT,
    scope_id: Optional[str] = None,
    increment: float = 1,
    dimensions: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Increment a counter metric.

    This is a convenience wrapper around track_metric for counters.
    """
    track_metric(
        db=db,
        metric_name=metric_name,
        value=increment,
        scope=scope,
        scope_id=scope_id,
        dimensions=dimensions,
    )


# =============================================================================
# Dashboard Queries
# =============================================================================

def get_dashboard_data(
    db: Session,
    scope: str,
    scope_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get dashboard data for a scope.

    Returns the latest snapshot plus real-time metrics.
    """
    # Get latest snapshot
    snapshot = db.query(AnalyticsSnapshot).filter(
        AnalyticsSnapshot.scope == scope,
        AnalyticsSnapshot.scope_id == scope_id,
    ).order_by(AnalyticsSnapshot.snapshot_date.desc()).first()

    if snapshot:
        data = snapshot.to_dict()
    else:
        # Generate real-time data if no snapshot
        data = generate_realtime_metrics(db, scope, scope_id)

    # Add real-time metrics (last hour)
    now = datetime.now(timezone.utc)
    hour_ago = now - timedelta(hours=1)

    recent_metrics = db.query(
        AnalyticsMetric.metric_name,
        func.sum(AnalyticsMetric.value).label('total')
    ).filter(
        AnalyticsMetric.scope == scope,
        AnalyticsMetric.scope_id == scope_id,
        AnalyticsMetric.timestamp >= hour_ago,
    ).group_by(AnalyticsMetric.metric_name).all()

    data["realtime"] = {m.metric_name: float(m.total) for m in recent_metrics}
    data["generated_at"] = now.isoformat()

    return data


def generate_realtime_metrics(
    db: Session,
    scope: str,
    scope_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate real-time metrics by querying actual data.

    Used when no snapshot is available.
    """
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Build filters based on scope
    if scope == MetricScope.TENANT and scope_id:
        user_filter = User.tenant_id == scope_id
        patient_filter = Patient.tenant_id == scope_id
        visit_filter = Visit.tenant_id == scope_id
    elif scope == MetricScope.REGIONAL and scope_id:
        # For regional, we need to join with tenant to get region
        user_filter = True  # Would need region join
        patient_filter = True
        visit_filter = True
    else:
        # Platform scope - all data
        user_filter = True
        patient_filter = True
        visit_filter = True

    # Count users
    total_users = db.query(func.count(User.id)).filter(user_filter).scalar() or 0
    active_users_24h = db.query(func.count(User.id)).filter(
        user_filter,
        User.updated_at >= day_ago  # Approximation
    ).scalar() or 0

    # Count patients
    total_patients = db.query(func.count(Patient.id)).filter(patient_filter).scalar() or 0
    new_patients_24h = db.query(func.count(Patient.id)).filter(
        patient_filter,
        Patient.created_at >= day_ago
    ).scalar() or 0

    # Count visits
    total_visits = db.query(func.count(Visit.id)).filter(visit_filter).scalar() or 0
    visits_24h = db.query(func.count(Visit.id)).filter(
        visit_filter,
        Visit.created_at >= day_ago
    ).scalar() or 0

    # Billing metrics (platform only)
    if scope == MetricScope.PLATFORM:
        total_tenants = db.query(func.count(Tenant.id)).scalar() or 0
        active_subs = db.query(func.count(Tenant.id)).filter(
            Tenant.subscription_status == 'active'
        ).scalar() or 0
    else:
        total_tenants = 0
        active_subs = 0

    return {
        "scope": scope,
        "scope_id": scope_id,
        "snapshot_date": now.isoformat(),
        "users": {
            "total": total_users,
            "active_24h": active_users_24h,
            "active_7d": 0,  # Would need more complex query
            "active_30d": 0,
        },
        "patients": {
            "total": total_patients,
            "new_24h": new_patients_24h,
            "new_7d": 0,
            "new_30d": 0,
        },
        "visits": {
            "total": total_visits,
            "count_24h": visits_24h,
            "count_7d": 0,
            "count_30d": 0,
        },
        "ai_usage": {
            "requests_24h": 0,
            "transcription_minutes_24h": 0,
        },
        "billing": {
            "total_tenants": total_tenants,
            "active_subscriptions": active_subs,
            "mrr": 0,
        },
        "extended": {},
    }


def get_metric_timeseries(
    db: Session,
    metric_name: str,
    scope: str,
    scope_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    period: str = MetricPeriod.DAILY,
    dimensions: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Get time-series data for a metric.

    Returns data points grouped by period.
    """
    if end_date is None:
        end_date = datetime.now(timezone.utc)
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    query = db.query(
        func.date_trunc(period.replace('ly', ''), AnalyticsMetric.timestamp).label('period'),
        func.sum(AnalyticsMetric.value).label('value'),
        func.sum(AnalyticsMetric.count).label('count'),
    ).filter(
        AnalyticsMetric.metric_name == metric_name,
        AnalyticsMetric.scope == scope,
        AnalyticsMetric.scope_id == scope_id,
        AnalyticsMetric.timestamp >= start_date,
        AnalyticsMetric.timestamp <= end_date,
    )

    # Apply dimension filters
    if dimensions:
        for key, value in dimensions.items():
            query = query.filter(
                AnalyticsMetric.dimensions[key].astext == str(value)
            )

    results = query.group_by('period').order_by('period').all()

    return [
        {
            "period": r.period.isoformat() if r.period else None,
            "value": float(r.value) if r.value else 0,
            "count": r.count or 0,
        }
        for r in results
    ]


def get_top_metrics(
    db: Session,
    metric_name: str,
    scope: str,
    group_by_dimension: str,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Get top values for a metric grouped by a dimension.

    Useful for leaderboards and rankings.
    """
    if end_date is None:
        end_date = datetime.now(timezone.utc)
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    results = db.query(
        AnalyticsMetric.dimensions[group_by_dimension].astext.label('dimension'),
        func.sum(AnalyticsMetric.value).label('value'),
    ).filter(
        AnalyticsMetric.metric_name == metric_name,
        AnalyticsMetric.scope == scope,
        AnalyticsMetric.timestamp >= start_date,
        AnalyticsMetric.timestamp <= end_date,
    ).group_by('dimension').order_by(
        func.sum(AnalyticsMetric.value).desc()
    ).limit(limit).all()

    return [
        {
            "dimension": r.dimension,
            "value": float(r.value) if r.value else 0,
        }
        for r in results
    ]


# =============================================================================
# Snapshot Generation
# =============================================================================

def create_snapshot(
    db: Session,
    scope: str,
    scope_id: Optional[str] = None,
) -> AnalyticsSnapshot:
    """
    Create a new analytics snapshot.

    Should be run periodically (e.g., hourly) by a background job.
    """
    data = generate_realtime_metrics(db, scope, scope_id)

    snapshot = AnalyticsSnapshot(
        scope=scope,
        scope_id=scope_id,
        snapshot_date=datetime.now(timezone.utc),
        total_users=data["users"]["total"],
        active_users_24h=data["users"]["active_24h"],
        active_users_7d=data["users"]["active_7d"],
        active_users_30d=data["users"]["active_30d"],
        total_patients=data["patients"]["total"],
        new_patients_24h=data["patients"]["new_24h"],
        new_patients_7d=data["patients"]["new_7d"],
        new_patients_30d=data["patients"]["new_30d"],
        total_visits=data["visits"]["total"],
        visits_24h=data["visits"]["count_24h"],
        visits_7d=data["visits"]["count_7d"],
        visits_30d=data["visits"]["count_30d"],
        ai_requests_24h=data["ai_usage"]["requests_24h"],
        transcription_minutes_24h=data["ai_usage"]["transcription_minutes_24h"],
        total_tenants=data["billing"]["total_tenants"],
        active_subscriptions=data["billing"]["active_subscriptions"],
        mrr=Decimal(str(data["billing"]["mrr"])),
        extended_metrics=data["extended"],
    )

    db.add(snapshot)
    return snapshot


def cleanup_old_metrics(
    db: Session,
    days_to_keep: int = 90,
) -> int:
    """
    Clean up old metric data.

    Keeps aggregated daily/weekly/monthly data longer.

    Returns:
        Number of deleted records
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

    # Delete hourly metrics older than cutoff
    deleted = db.query(AnalyticsMetric).filter(
        AnalyticsMetric.period == MetricPeriod.HOURLY,
        AnalyticsMetric.timestamp < cutoff,
    ).delete()

    logger.info(f"Cleaned up {deleted} old hourly metrics")
    return deleted


# =============================================================================
# Comparison Utilities
# =============================================================================

def get_metric_comparison(
    db: Session,
    metric_name: str,
    scope: str,
    scope_id: Optional[str] = None,
    current_start: datetime = None,
    current_end: datetime = None,
) -> Dict[str, Any]:
    """
    Get metric comparison between current and previous period.

    Returns current value, previous value, and change percentage.
    """
    if current_end is None:
        current_end = datetime.now(timezone.utc)
    if current_start is None:
        current_start = current_end - timedelta(days=7)

    period_length = current_end - current_start
    previous_start = current_start - period_length
    previous_end = current_start

    # Current period value
    current = db.query(func.sum(AnalyticsMetric.value)).filter(
        AnalyticsMetric.metric_name == metric_name,
        AnalyticsMetric.scope == scope,
        AnalyticsMetric.scope_id == scope_id,
        AnalyticsMetric.timestamp >= current_start,
        AnalyticsMetric.timestamp <= current_end,
    ).scalar() or 0

    # Previous period value
    previous = db.query(func.sum(AnalyticsMetric.value)).filter(
        AnalyticsMetric.metric_name == metric_name,
        AnalyticsMetric.scope == scope,
        AnalyticsMetric.scope_id == scope_id,
        AnalyticsMetric.timestamp >= previous_start,
        AnalyticsMetric.timestamp < previous_end,
    ).scalar() or 0

    # Calculate change
    current_val = float(current)
    previous_val = float(previous)

    if previous_val > 0:
        change_pct = ((current_val - previous_val) / previous_val) * 100
    elif current_val > 0:
        change_pct = 100
    else:
        change_pct = 0

    return {
        "metric_name": metric_name,
        "current_value": current_val,
        "previous_value": previous_val,
        "change_absolute": current_val - previous_val,
        "change_percent": round(change_pct, 2),
        "trend": "up" if change_pct > 0 else "down" if change_pct < 0 else "flat",
        "period": {
            "current_start": current_start.isoformat(),
            "current_end": current_end.isoformat(),
            "previous_start": previous_start.isoformat(),
            "previous_end": previous_end.isoformat(),
        },
    }
