# scenario-id: INC-1/SC-1
"""Driver: GET /api/incidents?status=open&service_id= must return 200 with filtered list."""

import json
import os

import httpx

base_url = os.environ.get("ASB_API_BASE", os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000"))


def main():
    # GET /api/incidents with status=open and empty service_id
    r = httpx.get(f"{base_url}/api/incidents", params={"status": "open", "service_id": ""})

    raw = r.text  # full JSON response as string

    parsed = {}
    try:
        parsed = r.json()
    except Exception:
        pass

    total = parsed.get("total", 0) if isinstance(parsed, dict) else 0

    # body as string allows "contains" checks on the raw JSON text
    # e.g. checking that "open" or "items" appears in the response body
    print(json.dumps({
        "status": r.status_code,
        "headers": dict(r.headers),
        "body": raw,
        "total": total,
    }))


if __name__ == "__main__":
    main()
