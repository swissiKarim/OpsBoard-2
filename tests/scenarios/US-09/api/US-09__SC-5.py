# scenario-id: US-09/SC-5
"""Backward status transition returns HTTP 400 with descriptive JSON error."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# 1. Create a service
svc_r = httpx.post(f"{base}/api/services", json={"name": "SC5-Svc", "team": "Ops"})
svc_id = svc_r.json()["id"]

# 2. Create an incident (status starts as 'open')
inc_r = httpx.post(
    f"{base}/api/incidents",
    json={"title": "SC5-Inc", "service_id": svc_id, "severity": "SEV2", "description": ""},
)
inc_id = inc_r.json()["id"]

# 3. Attempt backward transition: open → resolved (skipping 'investigating')
r = httpx.post(
    f"{base}/api/incidents/{inc_id}/status",
    json={"status": "resolved", "author": "tester", "comment": "skip step"},
)
print(json.dumps({
    "status_code": r.status_code,
    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text,
}))
