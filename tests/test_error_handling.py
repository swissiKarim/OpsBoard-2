"""Tests for REST API error handling – US-09.

Covers:
  AC-1: 404 for unknown service/incident IDs
  AC-2: 422 with per-field errors for invalid bodies
  AC-3: 400 for backward status transitions
  AC-4: GET /docs returns 200 with Swagger UI
  AC-5: GET /openapi.json returns valid OpenAPI schema
"""

import pytest


# ---------------------------------------------------------------------------
# AC-1: 404 for unknown IDs
# ---------------------------------------------------------------------------

def test_get_service_unknown_id_returns_404(client):
    r = client.get("/api/services/999999")
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body


def test_get_incident_unknown_id_returns_404(client):
    r = client.get("/api/incidents/999999")
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body


def test_put_service_unknown_id_returns_404(client):
    r = client.put("/api/services/999999", json={"name": "X", "description": "", "team": ""})
    assert r.status_code == 404
    assert "detail" in r.json()


def test_delete_service_unknown_id_returns_404(client):
    r = client.delete("/api/services/999999")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_put_incident_unknown_id_returns_404(client):
    r = client.put("/api/incidents/999999", json={"title": "x"})
    assert r.status_code == 404
    assert "detail" in r.json()


def test_status_transition_unknown_incident_returns_404(client):
    r = client.post(
        "/api/incidents/999999/status",
        json={"status": "investigating", "author": "op", "comment": ""},
    )
    assert r.status_code == 404
    assert "detail" in r.json()


# ---------------------------------------------------------------------------
# AC-2: 422 with per-field errors for invalid/missing required fields
# ---------------------------------------------------------------------------

def test_post_incident_missing_required_fields_returns_422(client):
    """POST /api/incidents with empty body → 422 with field errors."""
    r = client.post("/api/incidents", json={})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body
    # Pydantic validation errors are a list of field-level issues
    assert isinstance(body["detail"], list)
    fields = [e.get("loc", []) for e in body["detail"]]
    # title and service_id are required
    assert any("title" in loc for loc in fields)
    assert any("service_id" in loc for loc in fields)


def test_post_service_missing_name_returns_422(client):
    """POST /api/services with missing name → 422."""
    r = client.post("/api/services", json={})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    fields = [e.get("loc", []) for e in body["detail"]]
    assert any("name" in loc for loc in fields)


def test_post_service_wrong_type_for_name_returns_422(client):
    """POST /api/services with non-string name → 422."""
    r = client.post("/api/services", json={"name": None})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body


def test_post_incident_invalid_service_id_type_returns_422(client):
    """POST /api/incidents with non-int service_id → 422."""
    r = client.post(
        "/api/incidents",
        json={"title": "T", "service_id": "not-an-int", "severity": "SEV1"},
    )
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body


# ---------------------------------------------------------------------------
# AC-3: 400 for backward / invalid status transitions
# ---------------------------------------------------------------------------

def _create_service(client, name="ErrSvc"):
    r = client.post("/api/services", json={"name": name, "team": "Ops"})
    assert r.status_code == 201
    return r.json()["id"]


def _create_incident(client, service_id, title="ErrInc"):
    r = client.post(
        "/api/incidents",
        json={"title": title, "service_id": service_id, "severity": "SEV2", "description": ""},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_backward_transition_open_to_resolved_returns_400(client):
    """Cannot jump from open → resolved; must go open → investigating first."""
    svc_id = _create_service(client, "BwdSvc1")
    inc_id = _create_incident(client, svc_id, "BwdInc1")
    r = client.post(
        f"/api/incidents/{inc_id}/status",
        json={"status": "resolved", "author": "op", "comment": "skip"},
    )
    assert r.status_code == 400
    body = r.json()
    assert "detail" in body
    assert body["detail"]  # non-empty descriptive message


def test_backward_transition_resolved_to_investigating_returns_400(client):
    """Cannot go backwards from resolved → investigating."""
    svc_id = _create_service(client, "BwdSvc2")
    inc_id = _create_incident(client, svc_id, "BwdInc2")
    # Advance to resolved
    client.post(
        f"/api/incidents/{inc_id}/status",
        json={"status": "investigating", "author": "op", "comment": ""},
    )
    client.post(
        f"/api/incidents/{inc_id}/status",
        json={"status": "resolved", "author": "op", "comment": ""},
    )
    # Attempt backward
    r = client.post(
        f"/api/incidents/{inc_id}/status",
        json={"status": "investigating", "author": "op", "comment": "back"},
    )
    assert r.status_code == 400
    body = r.json()
    assert "detail" in body


def test_same_status_transition_returns_400(client):
    """Cannot transition to the same status."""
    svc_id = _create_service(client, "BwdSvc3")
    inc_id = _create_incident(client, svc_id, "BwdInc3")
    r = client.post(
        f"/api/incidents/{inc_id}/status",
        json={"status": "open", "author": "op", "comment": "noop"},
    )
    assert r.status_code == 400
    assert "detail" in r.json()


# ---------------------------------------------------------------------------
# AC-4: GET /docs serves Swagger UI
# ---------------------------------------------------------------------------

def test_get_docs_returns_200(client):
    r = client.get("/docs")
    assert r.status_code == 200
    assert "swagger" in r.text.lower()


# ---------------------------------------------------------------------------
# AC-5: GET /openapi.json returns valid OpenAPI schema
# ---------------------------------------------------------------------------

def test_get_openapi_json_returns_schema(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    assert "openapi" in body
    assert body["openapi"].startswith("3.")
    assert "info" in body
    assert "paths" in body
