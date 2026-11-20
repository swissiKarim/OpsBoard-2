# scenario-id: US-10/SC-4
"""SC-4: Dashboard KPI tiles show non-zero values after seeding.
then={status_code equals 200; body contains "<svg"}
"""

import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/", timeout=15, follow_redirects=True)

print(json.dumps({
    "status": resp.status_code,
    "headers": dict(resp.headers),
    "body": resp.text,
}))
