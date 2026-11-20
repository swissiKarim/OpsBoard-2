# scenario-id: US-10/SC-3
"""SC-3: After seeding GET /api/incidents returns exactly 25 incidents.
then={status_code equals 200; body.total equals 25}
"""

import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/api/incidents", timeout=15)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.json(),
}))
