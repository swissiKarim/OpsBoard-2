# scenario-id: US-02/SC-1
"""SC-1: ORM models are created and DB migrates on startup.
Calls GET /api/services/db-tables and checks the expected table names exist.
then={tables contains "service"; tables contains "incident"; tables contains "timeline_entry"}
"""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

try:
    resp = httpx.get(f"{base_url}/api/services/db-tables", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # tables is a comma-separated string from the API, e.g. "incident,service,timeline_entry"
    tables = data.get("tables", "")
except Exception as exc:
    print(json.dumps({"error": str(exc), "tables": ""}))
    sys.exit(1)

# Platform evaluates `tables contains "service"` as substring check on this string
print(json.dumps({"tables": tables}))
