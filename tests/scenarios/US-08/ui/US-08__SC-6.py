# scenario-id: US-08/SC-6
"""SC-6: Submitting valid modal form creates incident via POST /incidents and closes modal."""
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url.rstrip("/") + "/incidents")
    page.wait_for_selector('[data-testid="btn-new-incident"]')
    page.click('[data-testid="btn-new-incident"]')
    page.wait_for_function(
        "document.querySelector('[data-testid=\"modal-new-incident\"]').classList.contains('open')",
        timeout=5000,
    )

    # Fill the form using fill/select_option
    page.fill('[data-testid="modal-incident-title"]', "Test Incident")

    # Select first available service option
    service_sel = page.locator('[data-testid="modal-incident-service"]')
    options = service_sel.locator('option').all()
    if options:
        first_val = options[0].get_attribute('value')
        if first_val:
            service_sel.select_option(value=first_val)

    # Select SEV2 severity
    page.locator('[data-testid="modal-incident-severity"]').select_option(value='SEV2')

    page.fill('[data-testid="modal-incident-description"]', "Test description")
    page.click('[data-testid="modal-submit-btn"]')

    # Wait for modal to close
    page.wait_for_function(
        "!document.querySelector('[data-testid=\"modal-new-incident\"]').classList.contains('open')",
        timeout=8000,
    )
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
