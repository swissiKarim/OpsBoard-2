"""Services router – CRUD for OpsBoard services."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session

from app import models  # noqa: F401 – ensures all models are registered on Base
from app.database import engine, get_db
from app.status_engine import compute_service_status

router = APIRouter(prefix="/api/services", tags=["services"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    team: str = ""


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    team: str
    computed_status: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helper: list all table names in DB
# ---------------------------------------------------------------------------


@router.get("/db-tables")
def db_tables():
    """Return list of table names – used by SC-1 migration check."""
    inspector = sa_inspect(engine)
    return {"tables": inspector.get_table_names()}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    services = db.query(models.Service).all()
    result = []
    for svc in services:
        status = compute_service_status(svc.id, db)
        svc.computed_status = status
        result.append(ServiceResponse.model_validate(svc))
    return result


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    svc.computed_status = compute_service_status(svc.id, db)
    return svc


@router.post("/", response_model=ServiceResponse, status_code=201)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    svc = models.Service(
        name=payload.name,
        description=payload.description,
        team=payload.team,
        computed_status="operational",
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    svc.computed_status = compute_service_status(svc.id, db)
    return svc


@router.get("/{service_id}/status")
def get_service_status(service_id: int, db: Session = Depends(get_db)):
    """Return computed status for a service – used by scenario drivers."""
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"result": compute_service_status(service_id, db)}
