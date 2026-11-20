# scenario-id: US-05/SC-6
"""SC-6: KPI tile elements and chart container have data-testid attributes.
then={body contains "data-testid=\"kpi-"; body contains "data-testid=\"chart-"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

resp = httpx.get(f"{base_url}/dashboard", timeout=15, follow_redirects=True)

print(json.dumps({
    "status_code": resp.status_code,
    "body": resp.text,
}))
