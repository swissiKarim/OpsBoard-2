# scenario-id: US-07/SC-1
"""SC-1: Sidebar is rendered on all pages with toggle button having data-testid.
then={body contains "data-testid=\"sidebar"; body contains "data-testid=\"sidebar-toggle"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/dashboard", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
