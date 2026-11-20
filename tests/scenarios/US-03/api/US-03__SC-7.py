# scenario-id: US-03/SC-7
"""SC-7: GET /api/services/{id}, PUT and DELETE are implemented."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

create_resp = httpx.post(
    f"{base}/api/services",
    json={"name": "SC7-Service", "description": "sc7 test", "team": "Infra"},
    timeout=10,
)
svc_id = create_resp.json()["id"]

get_resp = httpx.get(f"{base}/api/services/{svc_id}", timeout=10)
body = get_resp.json()

print(json.dumps({
    "status_code": get_resp.status_code,
    "body": body,
}))
