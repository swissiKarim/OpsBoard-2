# scenario-id: US-04/SC-4
"""SC-4: POST /incidents/{id}/status advances open to investigating and creates timeline entry.
then={status_code equals 200; body.status equals "investigating"; timeline_entry_created equals true}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

svc_resp = httpx.post(
    f"{base_url}/api/services/",
    json={"name": "SC4-Service", "description": "", "team": "ops"},
    timeout=15,
    follow_redirects=True,
)
svc_id = svc_resp.json()["id"]

inc_resp = httpx.post(
    f"{base_url}/api/incidents/",
    json={"title": "SC-4 Transition Test", "service_id": svc_id, "severity": "SEV2", "description": ""},
    timeout=15,
    follow_redirects=True,
)
inc_id = inc_resp.json()["id"]

trans_resp = httpx.post(
    f"{base_url}/api/incidents/{inc_id}/status",
    json={"status": "investigating", "author": "operator", "comment": "Starting investigation"},
    timeout=15,
    follow_redirects=True,
)

body = trans_resp.json() if trans_resp.status_code == 200 else {}

detail_resp = httpx.get(f"{base_url}/incidents/{inc_id}", timeout=15, follow_redirects=True)
timeline_entry_created = "investigating" in detail_resp.text if detail_resp.status_code == 200 else False

print(json.dumps({
    "status_code": trans_resp.status_code,
    "body": body,
    "timeline_entry_created": timeline_entry_created,
}))
