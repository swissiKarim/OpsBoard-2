# scenario-id: US-02/SC-6
"""SC-6: Service status transitions from outage to operational after SEV1 resolved.
then={result equals "operational"}
"""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

client = httpx.Client(base_url=base_url, timeout=10)

try:
    # Create a service
    svc_resp = client.post("/api/services/", json={"name": "SC6-Service", "team": "ops"})
    svc_resp.raise_for_status()
    svc_id = svc_resp.json()["id"]

    # Create an open SEV1 incident → outage
    inc_resp = client.post("/api/incidents/", json={
        "title": "SC6 SEV1 incident",
        "service_id": svc_id,
        "severity": "SEV1",
        "status": "open",
    })
    inc_resp.raise_for_status()
    inc_id = inc_resp.json()["id"]

    # Resolve the SEV1 incident
    resolve_resp = client.patch(f"/api/incidents/{inc_id}/status", json={
        "status": "resolved",
        "author": "operator",
        "comment": "Issue fixed",
    })
    resolve_resp.raise_for_status()

    # Check service status again → operational
    after = client.get(f"/api/services/{svc_id}/status")
    after.raise_for_status()
    result = after.json().get("result")

except Exception as exc:
    print(json.dumps({"error": str(exc), "result": "error"}))
    sys.exit(1)

print(json.dumps({"result": result}))
