# scenario-id: US-06/SC-8
"""SC-8: Full-text search on title filters incident results.
then={status_code equals 200; body.items[0].title contains "database"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Seed a service and a known incident with "database" in the title
svc_resp = httpx.post(
    f"{base_url}/api/services",
    json={"name": "SC8-Svc", "description": "", "team": ""},
    timeout=15,
)
svc_id = svc_resp.json()["id"] if svc_resp.status_code == 201 else 1

httpx.post(
    f"{base_url}/api/incidents",
    json={
        "title": "database connection failure",
        "service_id": svc_id,
        "severity": "SEV2",
        "description": "Cannot reach the database",
    },
    timeout=15,
)

# Search by q=database via API
resp = httpx.get(
    f"{base_url}/api/incidents",
    params={"q": "database", "sort": "id_desc", "page": 1},
    timeout=15,
)

body = resp.json()

print(json.dumps({
    "status_code": resp.status_code,
    "body": body,
}))
