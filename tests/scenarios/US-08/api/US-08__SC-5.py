# scenario-id: US-08/SC-5
"""SC-5: Modal HTML includes focus-trap mechanism (modal-new-incident present in HTML)."""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))
url = base_url.rstrip("/") + "/incidents"

req = urllib.request.Request(url, headers={"Accept": "text/html"})
with urllib.request.urlopen(req) as resp:
    body = resp.read().decode("utf-8")
    status = resp.status

print(json.dumps({"status": status, "body": body}))
