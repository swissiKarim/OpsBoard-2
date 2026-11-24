# scenario-id: INC-1/SC-1
"""Driver: GET /api/incidents?status=open&service_id= must return 200 with filtered list."""

import json
import os
import sys

import requests

base_url = os.environ.get("ASB_API_BASE", os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000"))


def main():
    # AC-1 + AC-4: GET /api/incidents with status=open and empty service_id
    r = requests.get(f"{base_url}/api/incidents", params={"status": "open", "service_id": ""})
    status_code = r.status_code

    body = {}
    try:
        body = r.json()
    except Exception:
        pass

    # All items in result must have status=open
    items = body.get("items", []) if isinstance(body, dict) else []
    all_open = all(item.get("status") == "open" for item in items)

    # AC-2: empty severity also accepted
    r2 = requests.get(f"{base_url}/api/incidents", params={"status": "open", "service_id": "", "severity": ""})
    status_code_2 = r2.status_code

    # AC-3: URL params preserved — status filter is applied
    r3 = requests.get(f"{base_url}/api/incidents", params={"service_id": ""})
    status_code_3 = r3.status_code

    print(json.dumps({
        "status_code": status_code,
        "status_code_empty_severity": status_code_2,
        "status_code_only_empty_service_id": status_code_3,
        "total": body.get("total", 0) if isinstance(body, dict) else 0,
        "all_items_open": all_open,
        "items_count": len(items),
    }))


if __name__ == "__main__":
    main()
