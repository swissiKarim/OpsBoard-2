# scenario-id: US-04/SC-8
"""SC-8: Service stays outage if second SEV1 still open after resolving first.
then={body.computed_status equals "outage"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create service
svc_resp = httpx.post(f"{base_url}/api/services", json={"name": "SC8-Service", "description": "", "team": "ops"}, timeout=15)
svc_id = svc_resp.json()["id"]

# Create two SEV1 incidents
inc1_resp = httpx.post(
    f"{base_url}/api/incidents",
    json={"title": "SC-8 SEV1 First", "service_id": svc_id, "severity": "SEV1", "description": ""},
    timeout=15,
)
inc1_id = inc1_resp.json()["id"]

inc2_resp = httpx.post(
    f"{base_url}/api/incidents",
    json={"title": "SC-8 SEV1 Second", "service_id": svc_id, "severity": "SEV1", "description": ""},
    timeout=15,
)
inc2_id = inc2_resp.json()["id"]  # noqa: F841 – kept for clarity

# Resolve the first SEV1 only
httpx.post(f"{base_url}/api/incidents/{inc1_id}/status",
           json={"status": "investigating", "author": "op", "comment": ""}, timeout=15)
httpx.post(f"{base_url}/api/incidents/{inc1_id}/status",
           json={"status": "resolved", "author": "op", "comment": "Fixed first"}, timeout=15)

# Second SEV1 still open – service must remain outage
svc_get = httpx.get(f"{base_url}/api/services/{svc_id}", timeout=15)
body = svc_get.json() if svc_get.status_code == 200 else {}

print(json.dumps({"body": body}))
