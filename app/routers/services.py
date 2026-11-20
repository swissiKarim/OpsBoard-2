"""Services router – CRUD for OpsBoard services (UI + REST API)."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models  # noqa: F401 – ensures all models are registered on Base
from app.database import get_db
from app.status_engine import compute_service_status

router = APIRouter(tags=["services"])
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    team: str = ""


class ServiceUpdate(BaseModel):
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


class ServiceListResponse(BaseModel):
    total: int
    items: list[ServiceResponse]


# ---------------------------------------------------------------------------
# Helper: list all table names in DB
# ---------------------------------------------------------------------------


@router.get("/api/services/db-tables", tags=["meta"])
def db_tables(db: Session = Depends(get_db)):
    """Return list of table names – used by SC-1 migration check."""
    from sqlalchemy import text

    rows = db.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    ).fetchall()
    table_names = [r[0] for r in rows]
    return {"tables": ",".join(table_names)}


# ---------------------------------------------------------------------------
# UI routes
# ---------------------------------------------------------------------------


@router.get("/services", response_class=HTMLResponse, tags=["services-ui"])
def list_services_ui(request: Request, db: Session = Depends(get_db)):
    """Render the services list page."""
    services = db.query(models.Service).all()
    for svc in services:
        svc.computed_status = compute_service_status(svc.id, db)
    return templates.TemplateResponse(
        request,
        "services/list.html",
        {"services": services},
    )


@router.get("/services/new", response_class=HTMLResponse, tags=["services-ui"])
def new_service_form(request: Request):
    """Render blank service creation form."""
    return templates.TemplateResponse(
        request,
        "services/form.html",
        {"service": None, "action": "/services", "method": "post"},
    )


@router.post("/services", tags=["services-ui"])
def create_service_ui(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    team: str = Form(""),
    db: Session = Depends(get_db),
):
    """Handle service creation form submission; redirect to list on success."""
    svc = models.Service(
        name=name,
        description=description,
        team=team,
        computed_status="operational",
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    svc.computed_status = compute_service_status(svc.id, db)
    db.commit()
    return RedirectResponse(url="/services", status_code=302)


@router.get("/services/{service_id}", response_class=HTMLResponse, tags=["services-ui"])
def get_service_ui(service_id: int, request: Request, db: Session = Depends(get_db)):
    """Render service detail page."""
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    svc.computed_status = compute_service_status(svc.id, db)
    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.service_id == service_id)
        .order_by(models.Incident.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request,
        "services/detail.html",
        {"service": svc, "incidents": incidents},
    )


@router.get("/services/{service_id}/edit", response_class=HTMLResponse, tags=["services-ui"])
def edit_service_form(service_id: int, request: Request, db: Session = Depends(get_db)):
    """Render service edit form."""
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    svc.computed_status = compute_service_status(svc.id, db)
    return templates.TemplateResponse(
        request,
        "services/form.html",
        {
            "service": svc,
            "action": f"/services/{service_id}",
            "method": "post",
        },
    )


@router.post("/services/{service_id}", tags=["services-ui"])
def update_service_ui(
    service_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    team: str = Form(""),
    db: Session = Depends(get_db),
):
    """Handle service edit form submission (POST from HTML form)."""
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    svc.name = name
    svc.description = description
    svc.team = team
    svc.computed_status = compute_service_status(svc.id, db)
    db.commit()
    return RedirectResponse(url="/services", status_code=302)


@router.post("/services/{service_id}/delete", tags=["services-ui"])
def delete_service_ui(service_id: int, db: Session = Depends(get_db)):
    """Delete service and its incidents via HTML form."""
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    # Delete related timeline entries first, then incidents, then service
    incidents = db.query(models.Incident).filter(models.Incident.service_id == service_id).all()
    for inc in incidents:
        db.query(models.TimelineEntry).filter(
            models.TimelineEntry.incident_id == inc.id
        ).delete()
        db.delete(inc)
    db.delete(svc)
    db.commit()
    return RedirectResponse(url="/services", status_code=302)


# ---------------------------------------------------------------------------
# REST API endpoints (/api/services)
# ---------------------------------------------------------------------------


@router.get("/api/services", response_model=list[ServiceResponse], tags=["services-api"])
def api_list_services(db: Session = Depends(get_db)):
    services = db.query(models.Service).all()
    result = []
    for svc in services:
        svc.computed_status = compute_service_status(svc.id, db)
        result.append(ServiceResponse.model_validate(svc))
    return result


@router.post("/api/services", response_model=ServiceResponse, status_code=201, tags=["services-api"])
def api_create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
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
    db.commit()
    return ServiceResponse.model_validate(svc)


@router.get("/api/services/{service_id}", response_model=ServiceResponse, tags=["services-api"])
def api_get_service(service_id: int, db: Session = Depends(get_db)):
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    svc.computed_status = compute_service_status(svc.id, db)
    return ServiceResponse.model_validate(svc)


@router.put("/api/services/{service_id}", response_model=ServiceResponse, tags=["services-api"])
def api_update_service(
    service_id: int, payload: ServiceUpdate, db: Session = Depends(get_db)
):
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    svc.name = payload.name
    svc.description = payload.description
    svc.team = payload.team
    svc.computed_status = compute_service_status(svc.id, db)
    db.commit()
    db.refresh(svc)
    return ServiceResponse.model_validate(svc)


@router.delete("/api/services/{service_id}", status_code=200, tags=["services-api"])
def api_delete_service(service_id: int, db: Session = Depends(get_db)):
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    # Delete related timeline entries then incidents then service
    incidents = db.query(models.Incident).filter(models.Incident.service_id == service_id).all()
    for inc in incidents:
        db.query(models.TimelineEntry).filter(
            models.TimelineEntry.incident_id == inc.id
        ).delete()
        db.delete(inc)
    db.delete(svc)
    db.commit()
    return {"deleted": True, "id": service_id}


@router.get("/api/services/{service_id}/status", tags=["services-api"])
def api_get_service_status(service_id: int, db: Session = Depends(get_db)):
    """Return computed status for a service."""
    svc = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"result": compute_service_status(service_id, db)}
