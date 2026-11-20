# scenario-id: US-04/SC-10
"""SC-10: All REST API incident endpoints return JSON.
then={status_code equals 200; headers.content-type contains "application/json"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create a service and incident to work with
svc_resp = httpx.post(f"{base_url}/api/services", json={"name": "SC10-Service", "description": "", "team": "ops"}, timeout=15)
svc_id = svc_resp.json()["id"]

httpx.post(
    f"{base_url}/api/incidents",
    json={"title": "SC-10 JSON Test", "service_id": svc_id, "severity": "SEV3", "description": ""},
    timeout=15,
)

# GET /api/incidents – check for JSON content-type
resp = httpx.get(f"{base_url}/api/incidents", timeout=15)
content_type = resp.headers.get("content-type", "")

print(json.dumps({
    "status_code": resp.status_code,
    "headers": {"content-type": content_type},
}))
