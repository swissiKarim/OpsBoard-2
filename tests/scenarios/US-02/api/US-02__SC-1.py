# scenario-id: US-02/SC-1
"""SC-1: ORM models are created and DB migrates on startup.
Verifies that service, incident and timeline_entry tables exist by calling
GET /api/services/db-tables which queries sqlite_master directly.
then={tables contains "service"; tables contains "incident"; tables contains "timeline_entry"}
"""

import json
import os
import time

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

tables = ""
last_error = ""

# Retry up to 3 times with 1s delay to handle startup timing
for attempt in range(3):
    try:
        resp = httpx.get(f"{base_url}/api/services/db-tables", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            raw = data.get("tables", "")
            if isinstance(raw, list):
                tables = ",".join(raw)
            else:
                tables = str(raw)
            break
        else:
            last_error = f"http_{resp.status_code}:{resp.text[:200]}"
            time.sleep(1)
    except Exception as exc:
        last_error = str(exc)
        time.sleep(1)

if not tables:
    tables = f"failed:{last_error}"

# Platform evaluates `tables contains "service"` as substring check on this string
print(json.dumps({"tables": tables}))
