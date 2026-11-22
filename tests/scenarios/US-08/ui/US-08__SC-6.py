# scenario-id: US-08/SC-6
"""SC-6: Submitting valid modal form creates incident via POST /incidents and closes modal."""
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url.rstrip("/") + "/incidents")
    page.wait_for_selector('[data-testid="btn-new-incident"]')
    page.click('[data-testid="btn-new-incident"]')
    page.wait_for_selector('[data-testid="modal-new-incident"].open', timeout=5000)

    # Fill the form
    page.fill('[data-testid="modal-incident-title"]', "Test Incident")
    # Click service select to pick the first option (already selected by default)
    page.click('[data-testid="modal-incident-service"]')
    page.keyboard.press("Escape")  # close dropdown
    page.click('[data-testid="modal-incident-severity"]')
    page.keyboard.press("Escape")  # close dropdown
    page.fill('[data-testid="modal-incident-description"]', "Test description")
    page.click('[data-testid="modal-submit-btn"]')

    # Wait for modal to close
    page.wait_for_selector('[data-testid="modal-new-incident"]:not(.open)', timeout=8000)
    modal_visible = page.is_visible('[data-testid="modal-new-incident"].open')
    screenshot(page, "US-08/SC-6")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": {
            "modal-new-incident": modal_visible,
        },
    }))
