# scenario-id: US-04/SC-9
"""SC-9: PUT /incidents/{id} updates title and description but not status or severity.
then={body.title equals "NewTitle"; body.description equals "NewDesc"; body.status equals "open"; body.severity equals "SEV2"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC9-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "Original Title", "service_id": svc_id, "severity": "SEV2", "description": "Original Desc"},
    timeout=15,
    follow_redirects=True,
)
inc_id = inc_resp.json()["id"]

resp = httpx.put(
    f"{base_url}/api/incidents/{inc_id}",
    json={"title": "NewTitle", "description": "NewDesc"},
    timeout=15,
    follow_redirects=True,
)

body = resp.json() if resp.status_code == 200 else {}

print(json.dumps({
    "status_code": resp.status_code,
    "body": body,
}))
