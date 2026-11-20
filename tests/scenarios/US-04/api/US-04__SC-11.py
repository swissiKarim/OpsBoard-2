# scenario-id: US-04/SC-11
"""SC-11: Incident pages carry data-testid attributes on all UI elements.
then={status_code equals 200; body contains "data-testid"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC11-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC-11 Testid Test", "service_id": svc_id, "severity": "SEV1", "description": ""},
    timeout=15,
    follow_redirects=True,
)
inc_id = inc_resp.json()["id"]

resp = httpx.get(f"{base_url}/incidents/{inc_id}", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text if resp.status_code == 200 else "",
}))
