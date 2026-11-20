# scenario-id: US-05/SC-4
"""SC-4: New incident via POST /api/incidents immediately reflected in dashboard counter.
then={status_code equals 200; body contains "open-incidents-count"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create a service to attach the incident to
svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC4-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

# Create a new incident
httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC4 Test Incident", "service_id": svc_id, "severity": "SEV2", "description": "Test"},
    timeout=15,
    follow_redirects=True,
)

# Now fetch the dashboard and check the counter is present
resp = httpx.get(f"{base_url}/dashboard", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
