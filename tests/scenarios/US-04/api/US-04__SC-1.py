# scenario-id: US-04/SC-1
"""SC-1: POST /incidents creates incident with open status and recalculates service status.
then={status_code equals 201; body.status equals "open"; body.severity equals "SEV1"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create a service (trailing slash, follow redirects)
svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC1-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

resp = httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC-1 Test Incident", "service_id": svc_id, "severity": "SEV1", "description": "Test"},
    timeout=15,
    follow_redirects=True,
)

body = resp.json() if resp.status_code in (200, 201) else {}
print(json.dumps({
    "status_code": resp.status_code,
    "body": body,
}))
