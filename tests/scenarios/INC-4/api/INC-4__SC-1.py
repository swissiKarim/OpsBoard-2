# scenario-id: INC-4/SC-1
"""Driver: Verify that whitespace-only incident titles are rejected (422)
and that a valid title is accepted, clarifying title validation behaviour.

The driver performs two calls:
  1. POST /api/incidents with a whitespace-only title  → must return 422
  2. POST /api/incidents with a valid title            → must return 2xx

If both assertions hold the driver reports status=200 (scenario passed).
"""

import json
import os

import httpx

base_url = os.environ.get("ASB_API_BASE", os.environ.get("ASB_SVC_WEB_URL", "http://localhost:8000"))


def _ensure_service(base_url: str) -> int:
    """Create a throwaway service and return its id."""
    r = httpx.post(f"{base_url}/api/services", json={"name": "INC4-ValidationSvc", "team": "Ops"})
    if r.status_code in (200, 201):
        return r.json()["id"]
    # Fallback: try to pick any existing service
    r2 = httpx.get(f"{base_url}/api/services")
    items = r2.json().get("items", []) if r2.status_code == 200 else []
    if items:
        return items[0]["id"]
    raise RuntimeError(f"Could not create or find a service: {r.status_code} {r.text}")


def main():
    errors = []

    # --- Step 1: whitespace-only title must be rejected with 422 ---
    try:
        svc_id = _ensure_service(base_url)
    except RuntimeError as e:
        print(json.dumps({"status": 500, "headers": {}, "body": {"error": str(e)}}))
        return

    r_invalid = httpx.post(
        f"{base_url}/api/incidents",
        json={"title": "   ", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    if r_invalid.status_code != 422:
        errors.append(
            f"whitespace title: expected 422, got {r_invalid.status_code}"
        )

    # --- Step 2: valid title must be accepted (2xx) ---
    r_valid = httpx.post(
        f"{base_url}/api/incidents",
        json={"title": "INC-4 Validation Check", "service_id": svc_id, "severity": "SEV2", "description": ""},
    )
    if r_valid.status_code not in (200, 201):
        errors.append(
            f"valid title: expected 2xx, got {r_valid.status_code}"
        )

    if errors:
        # Scenario failed — report a non-200 status so the platform marks it red
        print(json.dumps({
            "status": 500,
            "headers": {},
            "body": {"errors": errors},
        }))
    else:
        # Both validations passed — scenario is green
        print(json.dumps({
            "status": 200,
            "headers": {},
            "body": {
                "whitespace_title_rejected": True,
                "whitespace_status": r_invalid.status_code,
                "valid_title_accepted": True,
                "valid_status": r_valid.status_code,
            },
        }))


if __name__ == "__main__":
    main()
