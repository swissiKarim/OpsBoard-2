# scenario-id: US-02/SC-2
"""SC-2: compute_service_status returns outage for open SEV1 incident."""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

client = httpx.Client(base_url=base_url, timeout=10)

try:
    # Create a service
    svc_resp = client.post("/api/services/", json={"name": "SC2-Service", "team": "ops"})
    svc_resp.raise_for_status()
    svc_id = svc_resp.json()["id"]

    # Create an open SEV1 incident
    inc_resp = client.post("/api/incidents/", json={
        "title": "SC2 SEV1 incident",
        "service_id": svc_id,
        "severity": "SEV1",
        "status": "open",
    })
    inc_resp.raise_for_status()

    # Check service status
    status_resp = client.get(f"/api/services/{svc_id}/status")
    status_resp.raise_for_status()
    result = status_resp.json().get("result")

except Exception as exc:
    print(json.dumps({"error": str(exc), "result": "error"}))
    sys.exit(1)

print(json.dumps({"status": status_resp.status_code, "body": {"result": result}}))
