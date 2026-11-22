# scenario-id: US-07/SC-9
"""SC-9: Empty state element present when incident list is empty.
then={body contains "empty"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Use a filter that won't match anything to trigger empty state
resp = httpx.get(
    f"{base_url}/incidents",
    params={"q": "ZZZZZZZZ_no_match_SC9_unique"},
    timeout=15,
    follow_redirects=True,
)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
