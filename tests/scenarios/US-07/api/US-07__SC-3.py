# scenario-id: US-07/SC-3
"""SC-3: CSS is served from repository without CDN; uses CSS variables.
then={status_code equals 200; body contains "--"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/static/css/main.css", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
