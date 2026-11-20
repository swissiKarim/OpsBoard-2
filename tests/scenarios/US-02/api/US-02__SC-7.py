# scenario-id: US-02/SC-7
"""SC-7: Service computed_status field is not directly writable via API.
Attempts to set computed_status to "manual_override" via create and checks
that the response does NOT reflect the injected value.
"""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

client = httpx.Client(base_url=base_url, timeout=10)

try:
    # Attempt to create a service with computed_status injected
    # The API schema (ServiceCreate) does not include computed_status,
    # so it should be ignored and always derived.
    svc_resp = client.post("/api/services/", json={
        "name": "SC7-Service",
        "team": "ops",
        "computed_status": "manual_override",  # must be ignored
    })
    svc_resp.raise_for_status()
    computed_status_in_response = svc_resp.json().get("computed_status", "")

except Exception as exc:
    print(json.dumps({"error": str(exc), "computed_status_in_response": "error"}))
    sys.exit(1)

print(json.dumps({
    "status": svc_resp.status_code,
    "body": {
        "computed_status_in_response": computed_status_in_response,
    },
}))
