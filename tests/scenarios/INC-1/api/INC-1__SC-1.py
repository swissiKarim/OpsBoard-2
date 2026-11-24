# scenario-id: INC-1/SC-1
"""Driver: GET /api/incidents?status=open&service_id= must return 200 with filtered list."""

import json
import os

import httpx

base_url = os.environ.get("ASB_API_BASE", os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000"))


def main():
    # GET /api/incidents with status=open and empty service_id
    r = httpx.get(f"{base_url}/api/incidents", params={"status": "open", "service_id": ""})

    # Return body as string so `contains` checks work on the raw JSON text
    print(json.dumps({
        "status": r.status_code,
        "headers": dict(r.headers),
        "body": r.text,
    }))


if __name__ == "__main__":
    main()
