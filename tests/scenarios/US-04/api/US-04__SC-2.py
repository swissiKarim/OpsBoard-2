# scenario-id: US-04/SC-2
"""SC-2: Service status becomes outage after SEV1 incident created.
then={body.computed_status equals "outage"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC2-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC-2 SEV1 Incident", "service_id": svc_id, "severity": "SEV1", "description": ""},
    timeout=15,
    follow_redirects=True,
)

svc_get = httpx.get(f"{base_url}/api/services/{svc_id}", timeout=15, follow_redirects=True)
body = svc_get.json() if svc_get.status_code == 200 else {}

print(json.dumps({"body": body}))
