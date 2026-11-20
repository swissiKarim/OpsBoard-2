# scenario-id: US-03/SC-2
"""SC-2: GET /services/{id} renders service detail page."""
import json
import os
import requests

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

# Create a service first so we have an id to look up
create_resp = requests.post(
    f"{base}/api/services",
    json={"name": "SC2-Service", "description": "detail test", "team": "Ops"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

resp = requests.get(f"{base}/services/{svc_id}", allow_redirects=True, timeout=10)
print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
