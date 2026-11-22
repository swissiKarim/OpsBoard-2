# scenario-id: US-07/SC-10
"""SC-10: HTML response contains responsive/card rendering hint for mobile tables.
then={body contains "card"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/incidents", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
