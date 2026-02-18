"""
Analytics API endpoints.

Provides analytics data for:
- Platform dashboards (super admin)
- Regional dashboards (regional admin)
- Tenant dashboards (tenant admin)
- Metric time-series queries
- Comparisons and trends
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging

from src.api.database import get_db
from src.api.auth.dependencies import (
    get_current_user,
    require_permissions,
    require_platform_admin,
)
from src.api.models.user import User
from src.api.models.role import Permissions, RoleScope
from src.api.models.analytics import MetricScope, MetricPeriod, METRIC_DEFINITIONS
from src.api.services import role_service
from src.api.services import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# =============================================================================
# Response Schemas
# =============================================================================

class DashboardResponse(BaseModel):
    """Dashboard data response."""
    scope: str
    scope_id: Optional[str]
    snapshot_date: Optional[str]
    users: Dict[str, Any]
    patients: Dict[str, Any]
    visits: Dict[str, Any]
    ai_usage: Dict[str, Any]
    billing: Dict[str, Any]
    extended: Dict[str, Any]
    realtime: Dict[str, float] = {}
    generated_at: str


class TimeSeriesPoint(BaseModel):
    """Single data point in time series."""
    period: str
    value: float
    count: int


class TimeSeriesResponse(BaseModel):
    """Time series data response."""
    metric_name: str
    scope: str
    scope_id: Optional[str]
    period: str
    data: List[TimeSeriesPoint]


class MetricComparisonResponse(BaseModel):
    """Metric comparison response."""
    metric_name: str
    current_value: float
    previous_value: float
    change_absolute: float
    change_percent: float
    trend: str  # up, down, flat
    period: Dict[str, str]


class MetricDefinitionResponse(BaseModel):
    """Metric definition."""
    name: str
    category: str
    display_name: str
    description: str
    unit: str
    aggregation: str


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    scope: str = Query(None, description="Scope (platform, regional, tenant). Defaults based on user role."),
    scope_id: Optional[str] = Query(None, description="Region or tenant ID"),
    current_user: User = Depends(require_permissions(Permissions.VIEW_ANALYTICS, Permissions.VIEW_OWN_ANALYTICS)),
    db: Session = Depends(get_db),
):
    """
    Get dashboard analytics data.

    Automatically determines scope based on user's role if not specified.
    """
    # Determine scope based on user role
    is_super = role_service.is_super_admin(db, current_user.id)

    if scope is None:
        if is_super:
            scope = MetricScope.PLATFORM
        elif current_user.tenant_id:
            scope = MetricScope.TENANT
            scope_id = current_user.tenant_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine analytics scope"
            )

    # Validate access
    if scope == MetricScope.PLATFORM and not is_super:
        # Check for platform-level analytics permission
        has_platform = role_service.has_permission(
            db, current_user.id, Permissions.VIEW_ALL_ANALYTICS,
            scope_type=RoleScope.PLATFORM
        )
        if not has_platform:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Platform analytics access required"
            )
    elif scope == MetricScope.TENANT:
        if not is_super and scope_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant's analytics"
            )
        scope_id = scope_id or current_user.tenant_id

    data = analytics_service.get_dashboard_data(db, scope, scope_id)
    return DashboardResponse(**data)


@router.get("/dashboard/tenant/{tenant_id}", response_model=DashboardResponse)
async def get_tenant_dashboard(
    tenant_id: str,
    current_user: User = Depends(require_permissions(Permissions.VIEW_ANALYTICS)),
    db: Session = Depends(get_db),
):
    """
    Get dashboard for a specific tenant.

    For tenant admins or super admins.
    """
    is_super = role_service.is_super_admin(db, current_user.id)

    if not is_super and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant's analytics"
        )

    data = analytics_service.get_dashboard_data(db, MetricScope.TENANT, tenant_id)
    return DashboardResponse(**data)


@router.get("/dashboard/platform", response_model=DashboardResponse)
async def get_platform_dashboard(
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    """
    Get platform-wide dashboard.

    Super admin only.
    """
    data = analytics_service.get_dashboard_data(db, MetricScope.PLATFORM, None)
    return DashboardResponse(**data)


# =============================================================================
# Time Series Endpoints
# =============================================================================

@router.get("/metrics/{metric_name}/timeseries", response_model=TimeSeriesResponse)
async def get_metric_timeseries(
    metric_name: str,
    scope: str = Query(MetricScope.TENANT, description="Scope"),
    scope_id: Optional[str] = Query(None, description="Scope ID"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    period: str = Query(MetricPeriod.DAILY, description="Aggregation period"),
    current_user: User = Depends(require_permissions(Permissions.VIEW_ANALYTICS, Permissions.VIEW_OWN_ANALYTICS)),
    db: Session = Depends(get_db),
):
    """
    Get time-series data for a metric.
    """
    # Validate metric exists
    if metric_name not in METRIC_DEFINITIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric '{metric_name}' not found"
        )

    # Validate access
    is_super = role_service.is_super_admin(db, current_user.id)

    if scope == MetricScope.TENANT:
        scope_id = scope_id or current_user.tenant_id
        if not is_super and scope_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif scope == MetricScope.PLATFORM and not is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform analytics access required"
        )

    data = analytics_service.get_metric_timeseries(
        db=db,
        metric_name=metric_name,
        scope=scope,
        scope_id=scope_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
    )

    return TimeSeriesResponse(
        metric_name=metric_name,
        scope=scope,
        scope_id=scope_id,
        period=period,
        data=[TimeSeriesPoint(**d) for d in data],
    )


@router.get("/metrics/{metric_name}/comparison", response_model=MetricComparisonResponse)
async def get_metric_comparison(
    metric_name: str,
    scope: str = Query(MetricScope.TENANT, description="Scope"),
    scope_id: Optional[str] = Query(None, description="Scope ID"),
    days: int = Query(7, ge=1, le=90, description="Comparison period in days"),
    current_user: User = Depends(require_permissions(Permissions.VIEW_ANALYTICS, Permissions.VIEW_OWN_ANALYTICS)),
    db: Session = Depends(get_db),
):
    """
    Get metric comparison between current and previous period.
    """
    # Validate metric
    if metric_name not in METRIC_DEFINITIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric '{metric_name}' not found"
        )

    # Validate access
    is_super = role_service.is_super_admin(db, current_user.id)

    if scope == MetricScope.TENANT:
        scope_id = scope_id or current_user.tenant_id
        if not is_super and scope_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif scope == MetricScope.PLATFORM and not is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform analytics access required"
        )

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    data = analytics_service.get_metric_comparison(
        db=db,
        metric_name=metric_name,
        scope=scope,
        scope_id=scope_id,
        current_start=start_date,
        current_end=end_date,
    )

    return MetricComparisonResponse(**data)


# =============================================================================
# Metric Definitions
# =============================================================================

@router.get("/metrics/definitions", response_model=List[MetricDefinitionResponse])
async def list_metric_definitions(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
):
    """
    List available metric definitions.
    """
    definitions = []

    for name, defn in METRIC_DEFINITIONS.items():
        if category and defn.get("category") != category:
            continue

        definitions.append(MetricDefinitionResponse(
            name=name,
            category=defn.get("category", "custom"),
            display_name=defn.get("display_name", name),
            description=defn.get("description", ""),
            unit=defn.get("unit", "count"),
            aggregation=defn.get("aggregation", "sum"),
        ))

    return definitions


# =============================================================================
# Top/Ranking Endpoints
# =============================================================================

@router.get("/top/{metric_name}")
async def get_top_metrics(
    metric_name: str,
    group_by: str = Query(..., description="Dimension to group by"),
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    """
    Get top values for a metric grouped by dimension.

    Platform admin only (for cross-tenant comparisons).
    """
    if metric_name not in METRIC_DEFINITIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric '{metric_name}' not found"
        )

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    data = analytics_service.get_top_metrics(
        db=db,
        metric_name=metric_name,
        scope=MetricScope.PLATFORM,
        group_by_dimension=group_by,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "metric_name": metric_name,
        "group_by": group_by,
        "period_days": days,
        "data": data,
    }


# =============================================================================
# Admin Endpoints
# =============================================================================

@router.post("/snapshots/generate")
async def generate_snapshot(
    scope: str = Query(MetricScope.PLATFORM),
    scope_id: Optional[str] = Query(None),
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    """
    Manually generate an analytics snapshot.

    Normally run by background jobs, but can be triggered manually.
    """
    snapshot = analytics_service.create_snapshot(db, scope, scope_id)
    db.commit()

    return {
        "message": "Snapshot generated",
        "snapshot_id": snapshot.id,
        "scope": scope,
        "scope_id": scope_id,
        "generated_at": snapshot.snapshot_date.isoformat(),
    }


@router.delete("/metrics/cleanup")
async def cleanup_old_metrics(
    days_to_keep: int = Query(90, ge=30, le=365),
    current_user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    """
    Clean up old hourly metrics.

    Keeps daily/weekly/monthly metrics.
    """
    deleted = analytics_service.cleanup_old_metrics(db, days_to_keep)
    db.commit()

    return {
        "message": f"Cleaned up {deleted} old metrics",
        "days_kept": days_to_keep,
    }
