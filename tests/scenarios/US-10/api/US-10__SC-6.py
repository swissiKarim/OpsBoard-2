# scenario-id: US-10/SC-6
"""SC-6: Seeded data contains all severities SEV1-SEV3.
then={body.total gte 1}
Returns total = minimum count across severities (all must be >= 1).
"""

import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/api/incidents", timeout=15)
data = resp.json()

items = data.get("items", [])
sev1_count = sum(1 for i in items if i.get("severity") == "SEV1")
sev2_count = sum(1 for i in items if i.get("severity") == "SEV2")
sev3_count = sum(1 for i in items if i.get("severity") == "SEV3")

# body.total gte 1: minimum across all severities must be >= 1
all_severities_covered = min(sev1_count, sev2_count, sev3_count)

print(json.dumps({
    "status_code": resp.status_code,
    "body": {
        "total": all_severities_covered,
        "sev1": sev1_count,
        "sev2": sev2_count,
        "sev3": sev3_count,
    },
}))
