# scenario-id: US-09/SC-3
"""POST /api/incidents with missing required fields returns 422 with field errors."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

r = httpx.post(f"{base}/api/incidents", json={}, follow_redirects=True)
print(json.dumps({
    "status_code": r.status_code,
    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text,
}))
