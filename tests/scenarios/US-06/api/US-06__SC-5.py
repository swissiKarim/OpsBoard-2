# scenario-id: US-06/SC-5
"""SC-5: Pagination controls rendered server-side with data-testid attributes.
then={body contains "data-testid=\"pagination"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Seed enough incidents to trigger pagination (need >20)
svc_resp = httpx.post(f"{base_url}/api/services", json={"name": "SC5-Svc", "description": "", "team": ""}, timeout=15)
svc_id = svc_resp.json()["id"] if svc_resp.status_code == 201 else 1

for i in range(22):
    httpx.post(f"{base_url}/api/incidents", json={
        "title": f"SC5 incident {i}",
        "service_id": svc_id,
        "severity": "SEV3",
        "description": "",
    }, timeout=15)

resp = httpx.get(
    f"{base_url}/incidents",
    params={"service_id": svc_id, "page": 1},
    timeout=15,
    follow_redirects=True,
)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
