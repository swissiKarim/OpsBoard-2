"""Tests for INC-4: Incident title whitespace validation.

Verifies that:
- A whitespace-only title is rejected with 422
- An empty title is rejected with 422
- A valid title (with surrounding spaces stripped concept) is accepted
"""


def _create_service(client, name="TitleValSvc"):
    r = client.post("/api/services", json={"name": name, "team": "Ops"})
    assert r.status_code in (200, 201)
    return r.json()["id"]


def test_whitespace_only_title_returns_422(client):
    """POST /api/incidents with title='   ' must return 422."""
    svc_id = _create_service(client, "WSTitleSvc")
    r = client.post(
        "/api/incidents",
        json={"title": "   ", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body


def test_empty_title_returns_422(client):
    """POST /api/incidents with title='' must return 422."""
    svc_id = _create_service(client, "EmptyTitleSvc")
    r = client.post(
        "/api/incidents",
        json={"title": "", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body


def test_tab_only_title_returns_422(client):
    """POST /api/incidents with title='\\t\\n' must return 422."""
    svc_id = _create_service(client, "TabTitleSvc")
    r = client.post(
        "/api/incidents",
        json={"title": "\t\n", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    assert r.status_code == 422


def test_valid_title_is_accepted(client):
    """POST /api/incidents with a proper title must succeed."""
    svc_id = _create_service(client, "ValidTitleSvc")
    r = client.post(
        "/api/incidents",
        json={"title": "Database latency spike", "service_id": svc_id, "severity": "SEV1", "description": ""},
    )
    assert r.status_code in (200, 201)
    body = r.json()
    assert body["title"] == "Database latency spike"


def test_title_with_leading_trailing_spaces_is_accepted(client):
    """POST /api/incidents with '  Real Title  ' must succeed (non-blank after strip)."""
    svc_id = _create_service(client, "SpacedTitleSvc")
    r = client.post(
        "/api/incidents",
        json={"title": "  Real Title  ", "service_id": svc_id, "severity": "SEV3", "description": ""},
    )
    assert r.status_code in (200, 201)
