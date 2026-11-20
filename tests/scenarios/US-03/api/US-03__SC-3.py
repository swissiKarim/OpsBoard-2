# scenario-id: US-03/SC-3
"""SC-3: POST /services creates a service and redirects to list."""
import json
import os

import httpx

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

resp = httpx.post(
    f"{base}/services",
    data={"name": "SC3-Service", "description": "redirect test", "team": "Platform"},
    follow_redirects=False,
    timeout=10,
)
print(json.dumps({
    "status_code": resp.status_code,
    "headers": dict(resp.headers),
}))
