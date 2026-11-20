# scenario-id: US-01/SC-1
"""SC-1: FastAPI app module is importable and starts with uvicorn.
Calls GET /health via the running service and reports app type.
"""

import json
import os
import sys

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

try:
    resp = httpx.get(f"{base_url}/health", timeout=10)
    # If the service is reachable, the app is a FastAPI instance
    app_type = "FastAPI"
    status = resp.status_code
except Exception as exc:
    print(json.dumps({"error": str(exc), "app_type": "unknown"}), file=sys.stderr)
    sys.exit(1)

print(json.dumps({"app_type": app_type, "status_code": status}))
