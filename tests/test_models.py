"""Tests for ORM model definitions and DB migration – covers US-02 AC-1."""

from sqlalchemy import inspect, text


def test_db_tables_created(engine):
    """All three ORM tables are created by init_db / Base.metadata.create_all."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "service" in tables, f"'service' table missing; found: {tables}"
    assert "incident" in tables, f"'incident' table missing; found: {tables}"
    assert "timeline_entry" in tables, f"'timeline_entry' table missing; found: {tables}"


def test_service_model_columns(engine):
    """Service table has the required columns."""
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("service")}
    assert "name" in cols
    assert "description" in cols
    assert "team" in cols
    assert "computed_status" in cols


def test_incident_model_columns(engine):
    """Incident table has the required columns."""
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("incident")}
    assert "title" in cols
    assert "service_id" in cols
    assert "severity" in cols
    assert "description" in cols
    assert "status" in cols


def test_timeline_entry_model_columns(engine):
    """TimelineEntry table has the required columns."""
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("timeline_entry")}
    assert "incident_id" in cols
    assert "author" in cols
    assert "comment" in cols


def test_db_tables_via_sqlite_master(db):
    """sqlite_master query returns expected table names (same as API endpoint)."""
    rows = db.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    ).fetchall()
    names = [r[0] for r in rows]
    assert "service" in names
    assert "incident" in names
    assert "timeline_entry" in names


def test_computed_status_not_in_service_create_schema():
    """ServiceCreate Pydantic schema does not expose computed_status."""
    from app.routers.services import ServiceCreate

    fields = ServiceCreate.model_fields
    assert "computed_status" not in fields, (
        "computed_status must not be a writable field on ServiceCreate"
    )
