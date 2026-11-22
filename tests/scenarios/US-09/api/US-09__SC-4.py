# scenario-id: US-09/SC-4
"""POST /api/services with invalid data returns 422 with per-field errors."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Send empty body – 'name' is required, so Pydantic must reject with 422
r = httpx.post(f"{base}/api/services", json={}, follow_redirects=True)
print(json.dumps({
    "status_code": r.status_code,
    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text,
}))
