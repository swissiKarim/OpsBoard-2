"""Dashboard router – placeholder for US-01 skeleton."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates_config import templates

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")
