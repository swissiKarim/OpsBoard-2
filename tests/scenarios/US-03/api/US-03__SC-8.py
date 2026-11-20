# scenario-id: US-03/SC-8
"""SC-8: Service form inputs have labels and data-testid; computed status not editable."""
import json
import os
import requests

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

# Create a service so the edit form exists
create_resp = requests.post(
    f"{base}/api/services",
    json={"name": "SC8-Service", "description": "form test", "team": "QA"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

# GET the edit form
resp = requests.get(f"{base}/services/{svc_id}/edit", timeout=10)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
