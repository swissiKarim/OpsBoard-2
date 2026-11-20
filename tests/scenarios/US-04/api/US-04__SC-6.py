# scenario-id: US-04/SC-6
"""SC-6: POST /incidents/{id}/status rejects investigating to open transition with HTTP 400.
then={status_code equals 400}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create service + incident
svc_resp = httpx.post(f"{base_url}/api/services", json={"name": "SC6-Service", "description": "", "team": "ops"}, timeout=15)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents",
    json={"title": "SC-6 Investigating→Open Test", "service_id": svc_id, "severity": "SEV2", "description": ""},
    timeout=15,
)
inc_id = inc_resp.json()["id"]

# Advance to investigating (valid)
httpx.post(
    f"{base_url}/api/incidents/{inc_id}/status",
    json={"status": "investigating", "author": "operator", "comment": ""},
    timeout=15,
)

# Try to go back to "open" from "investigating" – must be rejected with 400
resp = httpx.post(
    f"{base_url}/api/incidents/{inc_id}/status",
    json={"status": "open", "author": "operator", "comment": "trying to reopen"},
    timeout=15,
)

print(json.dumps({"status_code": resp.status_code}))
