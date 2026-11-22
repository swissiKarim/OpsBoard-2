"""Incidents router – CRUD and status machine for OpsBoard incidents."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.status_engine import compute_service_status
from app.templates_config import templates

router = APIRouter(tags=["incidents"])

PAGE_SIZE = 20

# ---------------------------------------------------------------------------
# Status machine – allowed forward transitions only
# ---------------------------------------------------------------------------

VALID_TRANSITIONS = {
    "open": "investigating",
    "investigating": "resolved",
}


def _next_allowed(current: str) -> str | None:
    return VALID_TRANSITIONS.get(current)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class IncidentCreate(BaseModel):
    title: str
    service_id: int
    severity: str  # SEV1 | SEV2 | SEV3
    description: str = ""


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    service_id: int
    severity: str
    status: str
    description: str

    model_config = {"from_attributes": True}


class StatusTransition(BaseModel):
    status: str
    author: str = "system"
    comment: str = ""


# ---------------------------------------------------------------------------
# UI routes
# ---------------------------------------------------------------------------


def _apply_incident_filters(query, q, status, severity, service_id):
    """Apply search/filter predicates to an Incident query."""
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(models.Incident.title.ilike(like), models.Incident.description.ilike(like))
        )
    if status:
        query = query.filter(models.Incident.status == status)
    if severity:
        query = query.filter(models.Incident.severity == severity)
    if service_id:
        query = query.filter(models.Incident.service_id == service_id)
    return query


def _apply_incident_sort(query, sort: str):
    sort_map = {
        "id_desc": models.Incident.id.desc(),
        "id_asc": models.Incident.id.asc(),
        "created_desc": models.Incident.created_at.desc(),
        "created_asc": models.Incident.created_at.asc(),
        "severity_asc": models.Incident.severity.asc(),
        "severity_desc": models.Incident.severity.desc(),
        "status_asc": models.Incident.status.asc(),
        "status_desc": models.Incident.status.desc(),
    }
    order = sort_map.get(sort, models.Incident.id.desc())
    return query.order_by(order)


@router.get("/incidents", response_class=HTMLResponse, include_in_schema=False)
def incidents_list_page(
    request: Request,
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    service_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("id_desc"),
    page: int = Query(1, ge=1),
):
    base_q = db.query(models.Incident)
    base_q = _apply_incident_filters(base_q, q, status, severity, service_id)
    base_q = _apply_incident_sort(base_q, sort)
    total = base_q.count()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    incidents = base_q.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()
    services = db.query(models.Service).all()
    return templates.TemplateResponse(
        request=request,
        name="incidents_list.html",
        context={
            "incidents": incidents,
            "services": services,
            "q": q or "",
            "status": status or "",
            "severity": severity or "",
            "service_id": service_id or "",
            "sort": sort or "id_desc",
            "page": page,
            "total": total,
            "total_pages": total_pages,
            "page_size": PAGE_SIZE,
        },
    )


@router.get("/incidents/{incident_id}", response_class=HTMLResponse, include_in_schema=False)
def incident_detail_page(incident_id: int, request: Request, db: Session = Depends(get_db)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return templates.TemplateResponse(
        request=request,
        name="incident_detail.html",
        context={"incident": inc, "timeline": inc.timeline_entries},
    )


# ---------------------------------------------------------------------------
# REST API endpoints
# ---------------------------------------------------------------------------


class IncidentListResponse(BaseModel):
    total: int
    items_count: int
    page: int
    total_pages: int
    items: list[IncidentResponse]


@router.get("/api/incidents", response_model=IncidentListResponse)
def list_incidents(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    service_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("id_desc"),
    page: int = Query(1, ge=1),
):
    base_q = db.query(models.Incident)
    base_q = _apply_incident_filters(base_q, q, status, severity, service_id)
    base_q = _apply_incident_sort(base_q, sort)
    total = base_q.count()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    items = base_q.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()
    return IncidentListResponse(
        total=total,
        items_count=len(items),
        page=page,
        total_pages=total_pages,
        items=items,
    )


@router.get("/api/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@router.post("/api/incidents", response_model=IncidentResponse, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    if payload.severity not in ("SEV1", "SEV2", "SEV3"):
        raise HTTPException(status_code=422, detail="severity must be SEV1, SEV2 or SEV3")

    svc = db.query(models.Service).filter(models.Service.id == payload.service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")

    inc = models.Incident(
        title=payload.title,
        service_id=payload.service_id,
        severity=payload.severity,
        description=payload.description,
        status="open",
    )
    db.add(inc)
    db.flush()  # get inc.id

    # Timeline entry for creation
    entry = models.TimelineEntry(
        incident_id=inc.id,
        author="system",
        comment="Incident created",
        status_from=None,
        status_to="open",
    )
    db.add(entry)
    db.commit()
    db.refresh(inc)

    # Recalculate service status immediately
    svc.computed_status = compute_service_status(svc.id, db)
    db.commit()

    return inc


@router.put("/api/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)):
    """Update editable fields (title, description) – status and severity are immutable."""
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if payload.title is not None:
        inc.title = payload.title
    if payload.description is not None:
        inc.description = payload.description

    db.commit()
    db.refresh(inc)
    return inc


@router.post("/api/incidents/{incident_id}/status", response_model=IncidentResponse)
def transition_status(
    incident_id: int,
    payload: StatusTransition,
    db: Session = Depends(get_db),
):
    """Advance incident status along open→investigating→resolved.

    Rejects any backward or sideways transition with HTTP 400.
    Creates a TimelineEntry with author, UTC timestamp and comment.
    """
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    allowed_next = _next_allowed(inc.status)
    if payload.status != allowed_next:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid transition: {inc.status!r} → {payload.status!r}. "
                f"Only {inc.status!r} → {allowed_next!r} is allowed."
            ),
        )

    old_status = inc.status
    inc.status = payload.status

    if payload.status == "resolved":
        inc.resolved_at = datetime.now(timezone.utc)

    entry = models.TimelineEntry(
        incident_id=incident_id,
        author=payload.author,
        comment=payload.comment,
        status_from=old_status,
        status_to=payload.status,
    )
    db.add(entry)
    db.commit()
    db.refresh(inc)

    # Recalculate service status
    svc = db.query(models.Service).filter(models.Service.id == inc.service_id).first()
    if svc:
        svc.computed_status = compute_service_status(svc.id, db)
        db.commit()

    return inc


# Keep PATCH for backwards compatibility (delegates to same logic)
@router.patch("/api/incidents/{incident_id}/status", response_model=IncidentResponse)
def transition_status_patch(
    incident_id: int,
    payload: StatusTransition,
    db: Session = Depends(get_db),
):
    return transition_status(incident_id, payload, db)


class CommentCreate(BaseModel):
    author: str = "operator"
    comment: str = ""


@router.post("/api/incidents/{incident_id}/comment", response_model=IncidentResponse)
def add_comment(
    incident_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
):
    """Append a plain comment to the timeline without changing status."""
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    entry = models.TimelineEntry(
        incident_id=incident_id,
        author=payload.author,
        comment=payload.comment,
        status_from=None,
        status_to=None,
    )
    db.add(entry)
    db.commit()
    db.refresh(inc)
    return inc
