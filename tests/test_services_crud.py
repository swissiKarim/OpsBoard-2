"""Tests for Service CRUD – UI and REST API (US-03)."""


# ---------------------------------------------------------------------------
# AC-1: GET /services renders Jinja2 list with status badges + data-testid rows
# ---------------------------------------------------------------------------

def test_get_services_list_html(client):
    r = client.get("/services")
    assert r.status_code == 200
    assert "data-testid" in r.text
    assert "services-list" in r.text


def test_get_services_list_contains_created_service(client):
    # Create via API
    client.post("/api/services", json={"name": "Alpha", "description": "d", "team": "T"})
    r = client.get("/services")
    assert r.status_code == 200
    assert "data-testid" in r.text
    assert "Alpha" in r.text


def test_services_list_has_status_badges(client):
    client.post("/api/services", json={"name": "BetaSvc", "team": "Ops"})
    r = client.get("/services")
    assert "badge" in r.text  # badge CSS class present


# ---------------------------------------------------------------------------
# AC-2: GET /services/{id} renders service detail page
# ---------------------------------------------------------------------------

def test_get_service_detail(client):
    rc = client.post("/api/services", json={"name": "DetailSvc", "description": "desc", "team": "T"})
    svc_id = rc.json()["id"]
    r = client.get(f"/services/{svc_id}")
    assert r.status_code == 200
    assert "DetailSvc" in r.text
    assert "service" in r.text.lower()


def test_get_service_detail_404(client):
    r = client.get("/services/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# AC-3: POST /services creates service and redirects to list
# ---------------------------------------------------------------------------

def test_post_services_redirects(client):
    r = client.post(
        "/services",
        data={"name": "RedirectSvc", "description": "x", "team": "T"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert "/services" in r.headers["location"]


def test_post_services_creates_in_db(client):
    client.post("/services", data={"name": "FormCreated", "team": "X"})
    r = client.get("/api/services")
    names = [s["name"] for s in r.json()["items"]]
    assert "FormCreated" in names


# ---------------------------------------------------------------------------
# AC-4: PUT /api/services/{id} updates name, description and team
# ---------------------------------------------------------------------------

def test_put_service_updates_fields(client):
    rc = client.post("/api/services", json={"name": "OldName", "description": "old", "team": "OldT"})
    svc_id = rc.json()["id"]
    r = client.put(
        f"/api/services/{svc_id}",
        json={"name": "Updated-Name", "description": "new desc", "team": "NewTeam"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Updated-Name"
    assert body["description"] == "new desc"
    assert body["team"] == "NewTeam"


def test_put_service_404(client):
    r = client.put("/api/services/99999", json={"name": "X", "description": "", "team": ""})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# AC-5: DELETE /api/services/{id} deletes service and related incidents
# ---------------------------------------------------------------------------

def test_delete_service_removes_service(client):
    rc = client.post("/api/services", json={"name": "ToDelete", "team": "X"})
    svc_id = rc.json()["id"]
    r = client.delete(f"/api/services/{svc_id}")
    assert r.status_code == 200
    # Verify gone
    r2 = client.get(f"/api/services/{svc_id}")
    assert r2.status_code == 404


def test_delete_service_removes_related_incidents(client):
    rc = client.post("/api/services", json={"name": "SvcWithInc", "team": "X"})
    svc_id = rc.json()["id"]
    # Create incident linked to service
    client.post(
        "/api/incidents",
        json={"title": "Inc1", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    # Delete service
    client.delete(f"/api/services/{svc_id}")
    # Incidents for that service should be gone
    all_inc = client.get("/api/incidents").json().get("items", [])
    assert all(i["service_id"] != svc_id for i in all_inc)


def test_delete_service_404(client):
    r = client.delete("/api/services/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# AC-6: GET /api/services and POST /api/services return JSON;
#        GET/PUT/DELETE /api/services/{id} implemented
# ---------------------------------------------------------------------------

def test_api_get_services_returns_json(client):
    r = client.get("/api/services")
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]


def test_api_post_service_returns_json(client):
    r = client.post("/api/services", json={"name": "JsonSvc", "team": "T"})
    assert r.status_code == 201
    assert "application/json" in r.headers["content-type"]
    assert r.json()["name"] == "JsonSvc"


def test_api_get_service_by_id(client):
    rc = client.post("/api/services", json={"name": "ByIdSvc", "team": "T"})
    svc_id = rc.json()["id"]
    r = client.get(f"/api/services/{svc_id}")
    assert r.status_code == 200
    assert r.json()["id"] == svc_id


def test_api_put_service(client):
    rc = client.post("/api/services", json={"name": "PutMe", "team": "T"})
    svc_id = rc.json()["id"]
    r = client.put(f"/api/services/{svc_id}", json={"name": "PutDone", "team": "T2"})
    assert r.status_code == 200
    assert r.json()["name"] == "PutDone"


def test_api_delete_service(client):
    rc = client.post("/api/services", json={"name": "DelMe", "team": "T"})
    svc_id = rc.json()["id"]
    r = client.delete(f"/api/services/{svc_id}")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# AC-7: Form inputs have labels and data-testid; computed status not editable
# ---------------------------------------------------------------------------

def test_new_service_form_has_labels_and_testids(client):
    r = client.get("/services/new")
    assert r.status_code == 200
    assert 'data-testid="input-name"' in r.text
    assert 'data-testid="input-description"' in r.text
    assert 'data-testid="input-team"' in r.text
    assert "<label" in r.text
    assert 'data-testid="label-name"' in r.text
    assert 'data-testid="label-description"' in r.text
    assert 'data-testid="label-team"' in r.text


def test_edit_form_shows_computed_status_as_read_only(client):
    rc = client.post("/api/services", json={"name": "ReadOnlySvc", "team": "T"})
    svc_id = rc.json()["id"]
    r = client.get(f"/services/{svc_id}/edit")
    assert r.status_code == 200
    # Status is displayed but not via an editable input
    assert "data-testid" in r.text
    assert "<label" in r.text
    assert 'display-computed-status' in r.text
    # No input[name=computed_status] or select for status
    assert 'name="computed_status"' not in r.text
    assert 'name="status"' not in r.text
