# scenario-id: US-03/SC-8
"""SC-8: Service form inputs have labels and data-testid; computed status not editable."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

create_resp = httpx.post(
    f"{base}/api/services",
    json={"name": "SC8-Service", "description": "form test", "team": "QA"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

resp = httpx.get(f"{base}/services/{svc_id}/edit", timeout=10)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
