# scenario-id: US-03/SC-3
"""SC-3: POST /services creates a service and redirects to list."""
import json
import os
import requests

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

# POST form data – do NOT follow redirect so we can inspect the 302
resp = requests.post(
    f"{base}/services",
    data={"name": "SC3-Service", "description": "redirect test", "team": "Platform"},
    allow_redirects=False,
    timeout=10,
)
print(json.dumps({
    "status_code": resp.status_code,
    "headers": dict(resp.headers),
}))
