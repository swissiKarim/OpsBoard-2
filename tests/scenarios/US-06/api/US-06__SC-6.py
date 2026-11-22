# scenario-id: US-06/SC-6
"""SC-6: Filter form inputs have labels and data-testid attributes.
then={body contains "<label"; body contains "data-testid"}
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
