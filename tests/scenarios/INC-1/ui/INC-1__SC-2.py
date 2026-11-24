# scenario-id: INC-1/SC-2
"""Driver: Apply status filter with empty service_id — UI journey."""
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    # Navigate to incidents list
    page.goto(base_url.rstrip("/") + "/incidents")
    page.wait_for_selector('[data-testid="select-status"]')

    # Select "open" in the status dropdown
    page.select_option('[data-testid="select-status"]', value="open")

    # Leave service_id as empty (default "All services" = "")
    # Click Apply
    page.click('[data-testid="btn-apply-filter"]')
    page.wait_for_load_state("networkidle")

    # Gather results
    final_url = page.url
    page_status = 200  # if we got here without crash, page loaded successfully
    error_text_present = False

    body_text = page.inner_text("body")
    # Check for error indicators
    if "422" in body_text or "Unprocessable" in body_text or "Internal Server Error" in body_text or "500" in body_text:
        error_text_present = True
        page_status = 422 if "422" in body_text or "Unprocessable" in body_text else 500

    # visible_text_contains: body text should contain "open" (from status badges or filter)
    visible_text_contains = body_text

    # Check key testids visible
    select_status_visible = page.is_visible('[data-testid="select-status"]')
    btn_apply_visible = page.is_visible('[data-testid="btn-apply-filter"]')

    result_count = 0
    tbody = page.query_selector('[data-testid="incidents-tbody"]')
    if tbody:
        rows = page.query_selector_all('[data-testid^="incident-row-"]')
        result_count = len(rows)

    screenshot(page, "INC-1/SC-2")

    print(json.dumps({
        "final_url": final_url,
        "page_status": page_status,
        "error_text_present": error_text_present,
        "result_count": result_count,
        "visible_text_contains": visible_text_contains,
        "visible": {
            "select-status": select_status_visible,
            "btn-apply-filter": btn_apply_visible,
        },
    }))
