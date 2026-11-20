# scenario-id: US-04/SC-5
"""SC-5: POST /incidents/{id}/status rejects backward transition with HTTP 400.
then={status_code equals 400}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC5-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC-5 Backward Test", "service_id": svc_id, "severity": "SEV1", "description": ""},
    timeout=15,
    follow_redirects=True,
)
inc_id = inc_resp.json()["id"]

# Advance to investigating (valid)
httpx.post(
    f"{base_url}/api/incidents/{inc_id}/status",
    json={"status": "investigating", "author": "operator", "comment": ""},
    timeout=15,
    follow_redirects=True,
)

# Backward transition: investigating → open (must be rejected with 400)
resp = httpx.post(
    f"{base_url}/api/incidents/{inc_id}/status",
    json={"status": "open", "author": "operator", "comment": ""},
    timeout=15,
    follow_redirects=True,
)

print(json.dumps({"status_code": resp.status_code}))
