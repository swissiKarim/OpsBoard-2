# scenario-id: US-04/SC-7
"""SC-7: Service status returns to operational after SEV1 resolved.
then={body.computed_status equals "operational"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create service + SEV1 incident
svc_resp = httpx.post(f"{base_url}/api/services", json={"name": "SC7-Service", "description": "", "team": "ops"}, timeout=15)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents",
    json={"title": "SC-7 SEV1 Resolve Test", "service_id": svc_id, "severity": "SEV1", "description": ""},
    timeout=15,
)
inc_id = inc_resp.json()["id"]

# Advance: open → investigating → resolved
httpx.post(f"{base_url}/api/incidents/{inc_id}/status",
           json={"status": "investigating", "author": "op", "comment": ""}, timeout=15)
httpx.post(f"{base_url}/api/incidents/{inc_id}/status",
           json={"status": "resolved", "author": "op", "comment": "Fixed"}, timeout=15)

# Fetch service status – should now be operational
svc_get = httpx.get(f"{base_url}/api/services/{svc_id}", timeout=15)
body = svc_get.json() if svc_get.status_code == 200 else {}

print(json.dumps({"body": body}))
