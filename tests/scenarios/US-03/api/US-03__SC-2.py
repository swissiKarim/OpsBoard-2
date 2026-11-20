# scenario-id: US-03/SC-2
"""SC-2: GET /services/{id} renders service detail page."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

create_resp = httpx.post(
    f"{base}/api/services",
    json={"name": "SC2-Service", "description": "detail test", "team": "Ops"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

resp = httpx.get(f"{base}/services/{svc_id}", follow_redirects=True, timeout=10)
print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
