# scenario-id: US-03/SC-4
"""SC-4: PUT /api/services/{id} updates name, description and team."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

create_resp = httpx.post(
    f"{base}/api/services",
    json={"name": "Original-Name", "description": "original desc", "team": "OldTeam"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

resp = httpx.put(
    f"{base}/api/services/{svc_id}",
    json={"name": "Updated-Name", "description": "updated desc", "team": "NewTeam"},
    timeout=10,
)
body = resp.json()
print(json.dumps({
    "status_code": resp.status_code,
    "body": body,
}))
