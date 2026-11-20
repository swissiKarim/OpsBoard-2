# scenario-id: US-01/SC-2
"""SC-2: GET /health returns 200 with body {"status": "ok"}."""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

try:
    resp = httpx.get(f"{base_url}/health", timeout=10)
except Exception as exc:
    print(json.dumps({"error": str(exc)}), file=sys.stderr)
    sys.exit(1)

try:
    body = resp.json()
except Exception:
    body = resp.text

print(json.dumps({"status_code": resp.status_code, "body": body}))
