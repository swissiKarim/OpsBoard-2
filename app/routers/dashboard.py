"""Dashboard router – KPI tiles, recent incidents, and inline-SVG bar chart."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.svg_builder import build_bar_chart
from app.templates_config import templates

router = APIRouter(tags=["dashboard"])


def _dashboard_context(db: Session) -> dict:
    """Compute all KPI values and return a template context dict."""
    now = datetime.now(timezone.utc)

    # --- KPI 1: count of open incidents --------------------------------------
    open_count = (
        db.query(models.Incident)
        .filter(models.Incident.status != "resolved")
        .count()
    )

    # --- KPI 2: services in degraded or outage -------------------------------
    affected_services_count = (
        db.query(models.Service)
        .filter(models.Service.computed_status.in_(["degraded", "outage"]))
        .count()
    )

    # --- KPI 3: mean resolution time (last 30 days) --------------------------
    cutoff_30d = now - timedelta(days=30)
    resolved_incidents = (
        db.query(models.Incident)
        .filter(
            models.Incident.status == "resolved",
            models.Incident.resolved_at != None,  # noqa: E711
            models.Incident.resolved_at >= cutoff_30d,
        )
        .all()
    )
    if resolved_incidents:
        durations = []
        for inc in resolved_incidents:
            resolved_at = inc.resolved_at
            created_at = inc.created_at
            # Make both timezone-aware for arithmetic
            if resolved_at.tzinfo is None:
                resolved_at = resolved_at.replace(tzinfo=timezone.utc)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            durations.append((resolved_at - created_at).total_seconds())
        mean_seconds = sum(durations) / len(durations)
        mean_resolution_hours = round(mean_seconds / 3600, 1)
    else:
        mean_resolution_hours = None

    # --- KPI 4: SVG bar chart – incidents per day, last 14 days --------------
    cutoff_14d = now - timedelta(days=14)
    recent_all = (
        db.query(models.Incident)
        .filter(models.Incident.created_at >= cutoff_14d)
        .all()
    )
    daily_counts: dict[str, int] = {}
    for inc in recent_all:
        created_at = inc.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        day_str = created_at.date().isoformat()
        daily_counts[day_str] = daily_counts.get(day_str, 0) + 1

    svg_chart = build_bar_chart(daily_counts, days=14)

    # --- Recently updated incidents (last 5) ---------------------------------
    recent_incidents = (
        db.query(models.Incident)
        .order_by(models.Incident.updated_at.desc())
        .limit(5)
        .all()
    )

    return {
        "open_incidents_count": open_count,
        "affected_services_count": affected_services_count,
        "mean_resolution_hours": mean_resolution_hours,
        "svg_chart": svg_chart,
        "recent_incidents": recent_incidents,
    }


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_dashboard(request: Request, db: Session = Depends(get_db)):
    ctx = _dashboard_context(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=ctx,
    )


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request, db: Session = Depends(get_db)):
    ctx = _dashboard_context(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=ctx,
    )
