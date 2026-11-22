# scenario-id: US-06/SC-1
"""SC-1: GET /incidents supports q, status, severity, service_id, sort and page query params.
then={status_code equals 200; body contains "SEV1"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# First seed a known incident so the response has SEV1 content
svc_resp = httpx.post(f"{base_url}/api/services", json={"name": "SC1-Svc", "description": "", "team": ""}, timeout=15)
svc_id = svc_resp.json()["id"] if svc_resp.status_code == 201 else 1

httpx.post(f"{base_url}/api/incidents", json={
    "title": "SC1 database outage",
    "service_id": svc_id,
    "severity": "SEV1",
    "description": "critical failure",
}, timeout=15)

resp = httpx.get(
    f"{base_url}/incidents",
    params={"q": "SC1", "status": "", "severity": "SEV1", "service_id": svc_id, "sort": "id_desc", "page": 1},
    timeout=15,
    follow_redirects=True,
)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
