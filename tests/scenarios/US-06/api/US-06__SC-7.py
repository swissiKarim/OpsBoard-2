# scenario-id: US-06/SC-7
"""SC-7: GET /api/incidents and GET /api/services accept query params and return paginated JSON.
then={status_code equals 200; headers.content-type contains "application/json"; body.total exists true}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Test /api/incidents
resp_inc = httpx.get(
    f"{base_url}/api/incidents",
    params={"q": "", "status": "", "severity": "", "sort": "id_desc", "page": 1},
    timeout=15,
)

body = resp_inc.json()

print(json.dumps({
    "status_code": resp_inc.status_code,
    "headers": {"content-type": resp_inc.headers.get("content-type", "")},
    "body": body,
}))
