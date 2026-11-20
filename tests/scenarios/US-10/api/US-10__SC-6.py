# scenario-id: US-10/SC-6
"""SC-6: Seeded data contains all severities SEV1-SEV3.
then={body.total gte 1}
Queries for SEV1 incidents (the rarest); if SEV1 exists, all severities are covered.
"""

import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/api/incidents", timeout=15)
data = resp.json()

# Count incidents per severity
items = data.get("items", [])
sev1_count = sum(1 for i in items if i.get("severity") == "SEV1")
sev2_count = sum(1 for i in items if i.get("severity") == "SEV2")
sev3_count = sum(1 for i in items if i.get("severity") == "SEV3")

# body.total gte 1 means: at least one incident with all three severities present.
# We return total = minimum count across severities (all must be >= 1).
all_severities_covered = min(sev1_count, sev2_count, sev3_count)

print(json.dumps({
    "status": resp.status_code,
    "headers": dict(resp.headers),
    "body": {
        "total": all_severities_covered,
        "sev1": sev1_count,
        "sev2": sev2_count,
        "sev3": sev3_count,
    },
}))
