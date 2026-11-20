# scenario-id: US-03/SC-1
"""SC-1: GET /services renders list with status badges and data-testid rows."""
import json
import os
import requests

base = os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000")

resp = requests.get(f"{base}/services", allow_redirects=True, timeout=10)
print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
