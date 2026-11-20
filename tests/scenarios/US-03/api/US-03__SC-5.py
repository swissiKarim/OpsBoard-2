# scenario-id: US-03/SC-5
"""SC-5: DELETE /api/services/{id} removes service and related incidents."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

svc_resp = httpx.post(
    f"{base}/api/services",
    json={"name": "SC5-Service", "description": "delete test", "team": "Ops"},
    timeout=10,
)
svc_id = svc_resp.json()["id"]

httpx.post(
    f"{base}/api/incidents/",
    json={"title": "SC5-Incident", "service_id": svc_id, "severity": "SEV2", "description": "test"},
    timeout=10,
    follow_redirects=True,
)

del_resp = httpx.delete(f"{base}/api/services/{svc_id}", timeout=10)

remaining = httpx.get(f"{base}/api/incidents/", timeout=10).json()
incidents_for_service = sum(1 for i in remaining if i["service_id"] == svc_id)

print(json.dumps({
    "status_code": del_resp.status_code,
    "incidents_for_service": incidents_for_service,
}))
