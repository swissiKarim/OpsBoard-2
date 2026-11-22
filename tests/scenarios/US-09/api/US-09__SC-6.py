# scenario-id: US-09/SC-6
"""GET /docs returns 200 and serves OpenAPI/Swagger UI."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

r = httpx.get(f"{base}/docs", follow_redirects=True)
print(json.dumps({
    "status_code": r.status_code,
    "body": r.text,
}))
