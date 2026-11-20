# scenario-id: US-10/SC-7
"""SC-7: Seeded data contains incidents with all three statuses.
then={body.total gte 1}
Returns total = minimum count across statuses (all must be >= 1).
"""

import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/api/incidents", timeout=15)
data = resp.json()

items = data.get("items", [])
open_count = sum(1 for i in items if i.get("status") == "open")
investigating_count = sum(1 for i in items if i.get("status") == "investigating")
resolved_count = sum(1 for i in items if i.get("status") == "resolved")

# body.total gte 1: all three statuses must be present
all_statuses_covered = min(open_count, investigating_count, resolved_count)

print(json.dumps({
    "status_code": resp.status_code,
    "body": {
        "total": all_statuses_covered,
        "open": open_count,
        "investigating": investigating_count,
        "resolved": resolved_count,
    },
}))
