# scenario-id: INC-1/SC-1
"""Driver: GET /api/incidents?status=open&service_id= must return 200 with filtered list."""

import json
import os

import httpx

base_url = os.environ.get("ASB_API_BASE", os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000"))


def main():
    # GET /api/incidents with status=open and empty service_id
    r = httpx.get(f"{base_url}/api/incidents", params={"status": "open", "service_id": ""})

    body = r.json()

    # Ensure items is a list (for contains checks on array elements)
    items = body.get("items", [])

    print(json.dumps({
        "status": r.status_code,
        "headers": dict(r.headers),
        "body": {
            "total": body.get("total", 0),
            "items_count": body.get("items_count", 0),
            "page": body.get("page", 1),
            "total_pages": body.get("total_pages", 1),
            "items": items,
        },
    }))


if __name__ == "__main__":
    main()
