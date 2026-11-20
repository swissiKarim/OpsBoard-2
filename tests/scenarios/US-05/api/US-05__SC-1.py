# scenario-id: US-05/SC-1
"""SC-1: GET / returns 200 and renders all four KPI tiles.
then={status_code equals 200; body contains "data-testid"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
