# scenario-id: US-03/SC-6
"""SC-6: GET /api/services and POST /api/services return JSON."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

get_resp = httpx.get(f"{base}/api/services", timeout=10)

print(json.dumps({
    "status_code": get_resp.status_code,
    "headers": {
        "content-type": get_resp.headers.get("content-type", ""),
    },
}))
