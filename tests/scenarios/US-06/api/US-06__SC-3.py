# scenario-id: US-06/SC-3
"""SC-3: GET /services supports q, status, sort and page query params.
then={status_code equals 200}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(
    f"{base_url}/services",
    params={"q": "", "status": "", "sort": "name_asc", "page": 1},
    timeout=15,
    follow_redirects=True,
)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
