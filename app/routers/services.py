"""Services router – CRUD placeholders for US-01 skeleton."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("/")
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()


@router.get("/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db)):
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc
