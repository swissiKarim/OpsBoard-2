# scenario-id: US-07/SC-4
"""SC-4: Status badges display text or icon in addition to colour.
then={body contains "outage"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Create a service and a SEV1 incident so outage status is rendered
svc_resp = httpx.post(
    f"{base_url}/api/services",
    json={"name": "SC4-BadgeSvc", "description": "badge test", "team": "ops"},
    timeout=15,
)
svc_id = svc_resp.json().get("id", 1) if svc_resp.status_code == 201 else 1

httpx.post(
    f"{base_url}/api/incidents",
    json={
        "title": "SC4 SEV1 outage test",
        "service_id": svc_id,
        "severity": "SEV1",
        "description": "causes outage badge",
    },
    timeout=15,
)

resp = httpx.get(f"{base_url}/services", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
