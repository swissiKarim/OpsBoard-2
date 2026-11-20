# scenario-id: US-03/SC-5
"""SC-5: DELETE /api/services/{id} removes service and related incidents."""
import json
import os
import requests

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

# Create a service
svc_resp = requests.post(
    f"{base}/api/services",
    json={"name": "SC5-Service", "description": "delete test", "team": "Ops"},
    timeout=10,
)
svc_id = svc_resp.json()["id"]

# Create an incident linked to that service
inc_resp = requests.post(
    f"{base}/api/incidents",
    json={"title": "SC5-Incident", "service_id": svc_id, "severity": "SEV2", "description": "test"},
    timeout=10,
)
inc_id = inc_resp.json()["id"]

# Delete the service
del_resp = requests.delete(f"{base}/api/services/{svc_id}", timeout=10)

# Check how many incidents remain for that service
remaining = requests.get(f"{base}/api/incidents", timeout=10).json()
incidents_for_service = sum(1 for i in remaining if i["service_id"] == svc_id)

print(json.dumps({
    "status_code": del_resp.status_code,
    "incidents_for_service": incidents_for_service,
}))
