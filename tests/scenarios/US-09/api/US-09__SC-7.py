# scenario-id: US-09/SC-7
"""GET /openapi.json returns valid OpenAPI schema JSON."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

r = httpx.get(f"{base}/openapi.json", follow_redirects=True)
print(json.dumps({
    "status_code": r.status_code,
    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text,
}))
