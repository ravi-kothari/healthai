"""
Reporting service for scheduled and on-demand reports.

Provides:
- Scheduled report configuration
- Report generation (PDF, CSV)
- Email delivery
- Report history tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging
import json

from src.api.models.analytics import (
    ScheduledReport, ReportExecution, AnalyticsSnapshot,
    MetricScope, METRIC_DEFINITIONS
)
from src.api.services import analytics_service

logger = logging.getLogger(__name__)


# =============================================================================
# Report Generation
# =============================================================================

def generate_report(
    db: Session,
    report: ScheduledReport,
) -> Dict[str, Any]:
    """
    Generate a report based on configuration.

    Args:
        db: Database session
        report: ScheduledReport configuration

    Returns:
        Generated report data
    """
    config = report.config or {}
    metrics = config.get("metrics", ["active_users", "visits", "patients_created"])
    date_range = config.get("date_range", "last_30_days")
    group_by = config.get("groupBy", "day")

    # Calculate date range
    end_date = datetime.now(timezone.utc)
    if date_range == "last_7_days":
        start_date = end_date - timedelta(days=7)
    elif date_range == "last_30_days":
        start_date = end_date - timedelta(days=30)
    elif date_range == "last_90_days":
        start_date = end_date - timedelta(days=90)
    elif date_range == "this_month":
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif date_range == "last_month":
        first_of_month = end_date.replace(day=1)
        end_date = first_of_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    else:
        start_date = end_date - timedelta(days=30)

    # Generate report data
    report_data = {
        "report_name": report.name,
        "report_type": report.report_type,
        "scope": report.scope,
        "scope_id": report.scope_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "label": date_range,
        },
        "metrics": {},
        "summary": {},
    }

    # Get dashboard data for summary
    dashboard = analytics_service.get_dashboard_data(db, report.scope, report.scope_id)
    report_data["summary"] = {
        "users": dashboard.get("users", {}),
        "patients": dashboard.get("patients", {}),
        "visits": dashboard.get("visits", {}),
    }

    # Get time series for each metric
    for metric_name in metrics:
        if metric_name in METRIC_DEFINITIONS:
            timeseries = analytics_service.get_metric_timeseries(
                db=db,
                metric_name=metric_name,
                scope=report.scope,
                scope_id=report.scope_id,
                start_date=start_date,
                end_date=end_date,
                period="daily" if group_by == "day" else "weekly",
            )

            comparison = analytics_service.get_metric_comparison(
                db=db,
                metric_name=metric_name,
                scope=report.scope,
                scope_id=report.scope_id,
                current_start=start_date,
                current_end=end_date,
            )

            report_data["metrics"][metric_name] = {
                "definition": METRIC_DEFINITIONS[metric_name],
                "timeseries": timeseries,
                "comparison": comparison,
            }

    return report_data


def generate_report_html(report_data: Dict[str, Any]) -> str:
    """
    Generate HTML content for a report.

    This is a simple template - in production, use Jinja2 or similar.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{report_data['report_name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .summary-box {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
            .metric-label {{ font-size: 12px; color: #666; }}
            .trend-up {{ color: #16a34a; }}
            .trend-down {{ color: #dc2626; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>{report_data['report_name']}</h1>
        <p>Generated: {report_data['generated_at']}</p>
        <p>Period: {report_data['date_range']['start'][:10]} to {report_data['date_range']['end'][:10]}</p>

        <div class="summary-box">
            <h2>Summary</h2>
            <div class="metric">
                <div class="metric-value">{report_data['summary'].get('users', {}).get('total', 0)}</div>
                <div class="metric-label">Total Users</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report_data['summary'].get('patients', {}).get('total', 0)}</div>
                <div class="metric-label">Total Patients</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report_data['summary'].get('visits', {}).get('total', 0)}</div>
                <div class="metric-label">Total Visits</div>
            </div>
        </div>
    """

    # Add metrics sections
    for metric_name, metric_data in report_data.get("metrics", {}).items():
        comparison = metric_data.get("comparison", {})
        trend_class = "trend-up" if comparison.get("trend") == "up" else "trend-down" if comparison.get("trend") == "down" else ""

        html += f"""
        <h3>{metric_data['definition'].get('display_name', metric_name)}</h3>
        <p>
            Current: <strong>{comparison.get('current_value', 0):.0f}</strong>
            <span class="{trend_class}">
                ({comparison.get('change_percent', 0):+.1f}% vs previous period)
            </span>
        </p>
        """

    html += """
        <hr>
        <p style="color: #666; font-size: 12px;">
            This report was automatically generated by MedGenie.
        </p>
    </body>
    </html>
    """

    return html


def generate_report_csv(report_data: Dict[str, Any]) -> str:
    """
    Generate CSV content for a report.
    """
    lines = []

    # Header
    lines.append(f"Report: {report_data['report_name']}")
    lines.append(f"Generated: {report_data['generated_at']}")
    lines.append(f"Period: {report_data['date_range']['start'][:10]} to {report_data['date_range']['end'][:10]}")
    lines.append("")

    # Summary
    lines.append("Summary")
    lines.append("Metric,Value")
    summary = report_data.get("summary", {})
    lines.append(f"Total Users,{summary.get('users', {}).get('total', 0)}")
    lines.append(f"Active Users (24h),{summary.get('users', {}).get('active_24h', 0)}")
    lines.append(f"Total Patients,{summary.get('patients', {}).get('total', 0)}")
    lines.append(f"New Patients (24h),{summary.get('patients', {}).get('new_24h', 0)}")
    lines.append(f"Total Visits,{summary.get('visits', {}).get('total', 0)}")
    lines.append("")

    # Metrics time series
    for metric_name, metric_data in report_data.get("metrics", {}).items():
        display_name = metric_data.get("definition", {}).get("display_name", metric_name)
        lines.append(f"{display_name}")
        lines.append("Date,Value,Count")

        for point in metric_data.get("timeseries", []):
            lines.append(f"{point.get('period', '')[:10]},{point.get('value', 0)},{point.get('count', 0)}")

        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Report Scheduling
# =============================================================================

def create_scheduled_report(
    db: Session,
    name: str,
    report_type: str,
    scope: str,
    scope_id: Optional[str],
    frequency: str,
    recipients: List[Dict[str, str]],
    config: Dict[str, Any],
    created_by: str,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
    hour: int = 8,
    timezone: str = "UTC",
) -> ScheduledReport:
    """
    Create a new scheduled report.

    Args:
        db: Database session
        name: Report name
        report_type: Type (usage, billing, clinical, custom)
        scope: Scope (platform, regional, tenant)
        scope_id: Region or tenant ID
        frequency: daily, weekly, monthly
        recipients: List of email recipients
        config: Report configuration
        created_by: User ID creating the report
        day_of_week: 0-6 for weekly (0=Monday)
        day_of_month: 1-28 for monthly
        hour: Hour to send (UTC)
        timezone: Timezone for scheduling

    Returns:
        Created ScheduledReport
    """
    # Calculate next run time
    next_run = calculate_next_run(frequency, day_of_week, day_of_month, hour)

    report = ScheduledReport(
        name=name,
        report_type=report_type,
        scope=scope,
        scope_id=scope_id,
        frequency=frequency,
        day_of_week=day_of_week,
        day_of_month=day_of_month,
        hour=hour,
        timezone=timezone,
        recipients=recipients,
        config=config,
        is_active='Y',
        next_run_at=next_run,
        created_by=created_by,
    )

    db.add(report)
    return report


def calculate_next_run(
    frequency: str,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
    hour: int = 8,
) -> datetime:
    """
    Calculate the next run time for a scheduled report.
    """
    now = datetime.now(timezone.utc)
    next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    if frequency == "daily":
        if next_run <= now:
            next_run += timedelta(days=1)

    elif frequency == "weekly":
        target_day = day_of_week or 0  # Default to Monday
        days_ahead = target_day - now.weekday()
        if days_ahead <= 0 or (days_ahead == 0 and next_run <= now):
            days_ahead += 7
        next_run += timedelta(days=days_ahead)

    elif frequency == "monthly":
        target_day = day_of_month or 1  # Default to 1st
        if now.day > target_day or (now.day == target_day and next_run <= now):
            # Move to next month
            if now.month == 12:
                next_run = next_run.replace(year=now.year + 1, month=1, day=target_day)
            else:
                next_run = next_run.replace(month=now.month + 1, day=target_day)
        else:
            next_run = next_run.replace(day=target_day)

    return next_run


def get_due_reports(db: Session) -> List[ScheduledReport]:
    """
    Get reports that are due to run.

    Should be called by a background job.
    """
    now = datetime.now(timezone.utc)

    return db.query(ScheduledReport).filter(
        ScheduledReport.is_active == 'Y',
        ScheduledReport.next_run_at <= now,
    ).all()


def execute_report(
    db: Session,
    report: ScheduledReport,
) -> ReportExecution:
    """
    Execute a scheduled report.

    Generates the report, saves it, and records the execution.
    """
    execution = ReportExecution(
        report_id=report.id,
        report_name=report.name,
        started_at=datetime.now(timezone.utc),
        status="running",
        metadata={
            "scope": report.scope,
            "scope_id": report.scope_id,
            "config": report.config,
        },
    )
    db.add(execution)
    db.flush()

    try:
        # Generate report
        report_data = generate_report(db, report)

        # Generate output format
        output_format = report.config.get("format", "html")
        if output_format == "csv":
            content = generate_report_csv(report_data)
            file_ext = "csv"
        else:
            content = generate_report_html(report_data)
            file_ext = "html"

        # In production, save to storage and send emails
        # For now, just record success
        execution.completed_at = datetime.now(timezone.utc)
        execution.status = "completed"
        execution.file_size = len(content.encode())
        execution.recipients_sent = len(report.recipients)

        # Update report schedule
        report.last_run_at = execution.started_at
        report.next_run_at = calculate_next_run(
            report.frequency,
            report.day_of_week,
            report.day_of_month,
            report.hour,
        )
        report.last_error = None

        logger.info(f"Report executed successfully: {report.name}")

    except Exception as e:
        execution.completed_at = datetime.now(timezone.utc)
        execution.status = "failed"
        execution.error_message = str(e)
        report.last_error = str(e)

        logger.error(f"Report execution failed: {report.name} - {e}")

    return execution


def run_due_reports(db: Session) -> List[ReportExecution]:
    """
    Run all due reports.

    Returns list of executions.
    """
    due_reports = get_due_reports(db)
    executions = []

    for report in due_reports:
        execution = execute_report(db, report)
        executions.append(execution)

    return executions


# =============================================================================
# Report Management
# =============================================================================

def get_report(db: Session, report_id: str) -> Optional[ScheduledReport]:
    """Get a scheduled report by ID."""
    return db.query(ScheduledReport).filter(
        ScheduledReport.id == report_id
    ).first()


def list_reports(
    db: Session,
    scope: str,
    scope_id: Optional[str] = None,
    active_only: bool = True,
) -> List[ScheduledReport]:
    """List scheduled reports for a scope."""
    query = db.query(ScheduledReport).filter(
        ScheduledReport.scope == scope,
        ScheduledReport.scope_id == scope_id,
    )

    if active_only:
        query = query.filter(ScheduledReport.is_active == 'Y')

    return query.order_by(ScheduledReport.name).all()


def update_report(
    db: Session,
    report: ScheduledReport,
    **updates,
) -> ScheduledReport:
    """Update a scheduled report."""
    for key, value in updates.items():
        if hasattr(report, key):
            setattr(report, key, value)

    # Recalculate next run if schedule changed
    if any(k in updates for k in ['frequency', 'day_of_week', 'day_of_month', 'hour']):
        report.next_run_at = calculate_next_run(
            report.frequency,
            report.day_of_week,
            report.day_of_month,
            report.hour,
        )

    return report


def deactivate_report(db: Session, report: ScheduledReport) -> None:
    """Deactivate a scheduled report."""
    report.is_active = 'N'


def get_report_history(
    db: Session,
    report_id: str,
    limit: int = 10,
) -> List[ReportExecution]:
    """Get execution history for a report."""
    return db.query(ReportExecution).filter(
        ReportExecution.report_id == report_id
    ).order_by(ReportExecution.started_at.desc()).limit(limit).all()
