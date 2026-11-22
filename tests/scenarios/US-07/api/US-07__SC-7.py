# scenario-id: US-07/SC-7
"""SC-7: CSS contains prefers-reduced-motion media query to disable animations.
then={body contains "prefers-reduced-motion"}
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
