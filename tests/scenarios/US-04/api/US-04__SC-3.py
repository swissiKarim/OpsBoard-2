# scenario-id: US-04/SC-3
"""SC-3: GET /incidents/{id} renders timeline and comment input.
then={status_code equals 200; body contains "timeline"; body contains "comment"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC3-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC-3 Detail Test", "service_id": svc_id, "severity": "SEV2", "description": "detail test"},
    timeout=15,
    follow_redirects=True,
)
inc_id = inc_resp.json()["id"]

resp = httpx.get(f"{base_url}/incidents/{inc_id}", timeout=15, follow_redirects=True)
body_text = resp.text if resp.status_code == 200 else ""

print(json.dumps({
    "status_code": resp.status_code,
    "body": body_text,
}))
