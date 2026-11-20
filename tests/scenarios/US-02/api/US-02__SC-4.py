# scenario-id: US-02/SC-4
"""SC-4: compute_service_status returns operational when no open incidents.
then={result equals "operational"}
"""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

client = httpx.Client(base_url=base_url, timeout=10)

try:
    # Create a service with no incidents
    svc_resp = client.post("/api/services/", json={"name": "SC4-Service", "team": "ops"})
    svc_resp.raise_for_status()
    svc_id = svc_resp.json()["id"]

    # Check service status (no incidents → operational)
    status_resp = client.get(f"/api/services/{svc_id}/status")
    status_resp.raise_for_status()
    result = status_resp.json().get("result")

except Exception as exc:
    print(json.dumps({"error": str(exc), "result": "error"}))
    sys.exit(1)

print(json.dumps({"result": result}))
