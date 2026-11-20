"""Incidents router – CRUD for OpsBoard incidents."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.status_engine import compute_service_status

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class IncidentCreate(BaseModel):
    title: str
    service_id: int
    severity: str  # SEV1 | SEV2 | SEV3
    description: str = ""
    status: str = "open"  # open | investigating | resolved


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
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@router.post("/", response_model=IncidentResponse, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    if payload.severity not in ("SEV1", "SEV2", "SEV3"):
        raise HTTPException(status_code=422, detail="severity must be SEV1, SEV2 or SEV3")
    if payload.status not in ("open", "investigating", "resolved"):
        raise HTTPException(status_code=422, detail="status must be open, investigating or resolved")
    # Verify service exists
    svc = db.query(models.Service).filter(models.Service.id == payload.service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")

    inc = models.Incident(
        title=payload.title,
        service_id=payload.service_id,
        severity=payload.severity,
        description=payload.description,
        status=payload.status,
    )
    db.add(inc)
    # Add timeline entry for initial status
    entry = models.TimelineEntry(
        incident=inc,
        author=payload.author if hasattr(payload, "author") else "system",
        comment="Incident created",
        status_from=None,
        status_to=payload.status,
    )
    db.add(entry)
    db.commit()
    db.refresh(inc)

    # Update service computed_status
    svc.computed_status = compute_service_status(svc.id, db)
    db.commit()

    return inc


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def transition_status(
    incident_id: int,
    payload: StatusTransition,
    db: Session = Depends(get_db),
):
    valid_statuses = ("open", "investigating", "resolved")
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"status must be one of {valid_statuses}")

    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_status = inc.status
    inc.status = payload.status

    if payload.status == "resolved":
        from sqlalchemy import func
        inc.resolved_at = func.now()

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

    # Update service computed_status
    svc = db.query(models.Service).filter(models.Service.id == inc.service_id).first()
    if svc:
        svc.computed_status = compute_service_status(svc.id, db)
        db.commit()

    return inc
