"""Incidents router – CRUD placeholders for US-01 skeleton."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("/")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()


@router.get("/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc
