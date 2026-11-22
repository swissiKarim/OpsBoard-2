# scenario-id: US-06/SC-2
"""SC-2: Incidents list paginates at 20 entries per page.
then={body.items_count lte 20}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/api/incidents", params={"page": 1}, timeout=15)

body = resp.json()

print(json.dumps({
    "status_code": resp.status_code,
    "body": body,
}))
