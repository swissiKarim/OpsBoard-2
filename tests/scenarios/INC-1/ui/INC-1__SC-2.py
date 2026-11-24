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

    # Leave service_id as the default empty value ("All services")
    # Click Apply filter button
    page.click('[data-testid="btn-apply-filter"]')
    page.wait_for_load_state("networkidle")

    # Determine page_status: check for error page markers
    # (HTTP error pages typically show h1/title with error text, not normal content)
    final_url = page.url

    # Check for error indicators via specific error page elements
    has_500 = page.query_selector('h1:has-text("500")') is not None
    has_422 = page.query_selector('h1:has-text("422")') is not None
    has_unprocessable = "Unprocessable Entity" in page.title()
    has_internal_error = "Internal Server Error" in page.title()

    error_text_present = has_500 or has_422 or has_unprocessable or has_internal_error

    if has_500 or has_internal_error:
        page_status = 500
    elif has_422 or has_unprocessable:
        page_status = 422
    else:
        page_status = 200

    body_text = page.inner_text("body")
    visible_text_contains = body_text

    # Count result rows
    result_count = 0
    rows = page.query_selector_all('[data-testid^="incident-row-"]')
    result_count = len(rows)

    # Check key testids visible
    select_status_visible = page.is_visible('[data-testid="select-status"]')
    btn_apply_visible = page.is_visible('[data-testid="btn-apply-filter"]')

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
