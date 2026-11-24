"""Regression tests – empty optional filter params must not cause 422.

Covers:
  AC-1: GET /incidents with status=open and empty service_id returns 200
  AC-2: Empty service_id and severity are treated as unset (no filter applied)
  AC-3: URL params preserved (checked via API equivalent)
  AC-4: GET /api/incidents accepts empty service_id without 422
"""


# ---------------------------------------------------------------------------
# AC-1 + AC-4: Empty service_id on both UI and API routes
# ---------------------------------------------------------------------------

def test_ui_incidents_empty_service_id_returns_200(client):
    """GET /incidents?status=open&service_id= must return 200, not 422."""
    r = client.get("/incidents?status=open&service_id=")
    assert r.status_code == 200


def test_api_incidents_empty_service_id_returns_200(client):
    """GET /api/incidents?service_id= must return 200 with valid JSON, not 422."""
    r = client.get("/api/incidents?service_id=")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body


def test_api_incidents_status_and_empty_service_id(client):
    """GET /api/incidents?status=open&service_id= filters by status without 422."""
    r = client.get("/api/incidents?status=open&service_id=")
    assert r.status_code == 200
    body = r.json()
    # All returned incidents must have status=open
    for item in body["items"]:
        assert item["status"] == "open"


# ---------------------------------------------------------------------------
# AC-2: Empty severity is also treated as unset
# ---------------------------------------------------------------------------

def test_api_incidents_empty_severity_returns_200(client):
    """GET /api/incidents?severity= must return 200, not 422."""
    r = client.get("/api/incidents?severity=")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body


def test_ui_incidents_empty_severity_returns_200(client):
    """GET /incidents?severity= must return 200."""
    r = client.get("/incidents?severity=")
    assert r.status_code == 200


def test_api_incidents_all_empty_optional_params(client):
    """All optional params empty → 200 with full unfiltered list."""
    r = client.get("/api/incidents?q=&status=&severity=&service_id=")
    assert r.status_code == 200
    body = r.json()
    assert "total" in body


# ---------------------------------------------------------------------------
# AC-3: URL params preserved — filter by status=open returns only open items
# ---------------------------------------------------------------------------

def test_api_incidents_status_filter_preserved(client):
    """status=open filter is correctly applied even when service_id is empty."""
    # Create a service and two incidents with different statuses
    svc_r = client.post("/api/services", json={"name": "FilterSvc", "team": "Ops"})
    assert svc_r.status_code == 201
    svc_id = svc_r.json()["id"]

    inc1_r = client.post(
        "/api/incidents",
        json={"title": "Open Inc", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    assert inc1_r.status_code == 201
    inc1_id = inc1_r.json()["id"]

    inc2_r = client.post(
        "/api/incidents",
        json={"title": "Investigating Inc", "service_id": svc_id, "severity": "SEV3", "description": ""},
    )
    assert inc2_r.status_code == 201
    inc2_id = inc2_r.json()["id"]
    # Advance inc2 to investigating
    client.post(
        f"/api/incidents/{inc2_id}/status",
        json={"status": "investigating", "author": "op", "comment": ""},
    )

    # Filter: status=open, empty service_id
    r = client.get("/api/incidents?status=open&service_id=")
    assert r.status_code == 200
    body = r.json()
    ids = [item["id"] for item in body["items"]]
    assert inc1_id in ids
    assert inc2_id not in ids


def test_api_incidents_valid_service_id_still_filters(client):
    """A real service_id value still filters correctly (regression guard)."""
    svc_r = client.post("/api/services", json={"name": "RealSvc", "team": "Ops"})
    assert svc_r.status_code == 201
    svc_id = svc_r.json()["id"]

    svc2_r = client.post("/api/services", json={"name": "OtherSvc", "team": "Ops"})
    assert svc2_r.status_code == 201
    svc2_id = svc2_r.json()["id"]

    inc_r = client.post(
        "/api/incidents",
        json={"title": "SvcInc", "service_id": svc_id, "severity": "SEV1", "description": ""},
    )
    assert inc_r.status_code == 201
    inc_id = inc_r.json()["id"]

    r = client.get(f"/api/incidents?service_id={svc_id}")
    assert r.status_code == 200
    ids = [item["id"] for item in r.json()["items"]]
    assert inc_id in ids

    r2 = client.get(f"/api/incidents?service_id={svc2_id}")
    assert r2.status_code == 200
    ids2 = [item["id"] for item in r2.json()["items"]]
    assert inc_id not in ids2
