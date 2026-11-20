# scenario-id: US-03/SC-4
"""SC-4: PUT /api/services/{id} updates name, description and team."""
import json
import os
import requests

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

# Create a service to update
create_resp = requests.post(
    f"{base}/api/services",
    json={"name": "Original-Name", "description": "original desc", "team": "OldTeam"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

# Update it via PUT
resp = requests.put(
    f"{base}/api/services/{svc_id}",
    json={"name": "Updated-Name", "description": "updated desc", "team": "NewTeam"},
    timeout=10,
)
body = resp.json()
print(json.dumps({
    "status_code": resp.status_code,
    "body": body,
}))
