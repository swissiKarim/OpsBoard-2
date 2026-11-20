"""OpsBoard – FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="OpsBoard",
    description="Operations dashboard for monitoring services and managing incidents.",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Static files & templates (paths created at scaffold time)
# ---------------------------------------------------------------------------

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
def health():
    """Return service health status."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

from fastapi.responses import RedirectResponse  # noqa: E402


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard")


# ---------------------------------------------------------------------------
# Routers (imported after app is created to avoid circular imports)
# ---------------------------------------------------------------------------

from app.routers import dashboard, incidents, services  # noqa: E402

app.include_router(services.router)
app.include_router(incidents.router)
app.include_router(dashboard.router)
