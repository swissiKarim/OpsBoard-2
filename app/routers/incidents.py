"""Incidents router – CRUD and status machine for OpsBoard incidents."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.status_engine import compute_service_status
from app.templates_config import templates

router = APIRouter(tags=["incidents"])

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


@router.get("/incidents", response_class=HTMLResponse, include_in_schema=False)
def incidents_list_page(request: Request, db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).order_by(models.Incident.id.desc()).all()
    services = db.query(models.Service).all()
    return templates.TemplateResponse(
        request=request,
        name="incidents_list.html",
        context={"incidents": incidents, "services": services},
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


@router.get("/api/incidents", response_model=list[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()


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
