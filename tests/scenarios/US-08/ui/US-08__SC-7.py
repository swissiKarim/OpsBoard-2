# scenario-id: US-08/SC-7
"""SC-7: Toast notification shown after successful incident creation."""
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url.rstrip("/") + "/incidents")
    page.wait_for_selector('[data-testid="btn-new-incident"]')
    page.click('[data-testid="btn-new-incident"]')
    page.wait_for_selector('[data-testid="modal-new-incident"].open', timeout=5000)

    # Fill the form
    page.fill('[data-testid="modal-incident-title"]', "Toast Test Incident")

    # Select first available service option
    service_sel = page.locator('[data-testid="modal-incident-service"]')
    options = service_sel.locator('option').all()
    if options:
        first_val = options[0].get_attribute('value')
        if first_val:
            service_sel.select_option(value=first_val)

    # Select SEV2 severity
    page.locator('[data-testid="modal-incident-severity"]').select_option(value='SEV2')

    page.fill('[data-testid="modal-incident-description"]', "desc")
    page.click('[data-testid="modal-submit-btn"]')

    # Wait for toast to appear
    page.wait_for_selector('[data-testid="toast-incident-created"]:not(.hidden)', timeout=8000)
    toast_visible = page.is_visible('[data-testid="toast-incident-created"]')
    screenshot(page, "US-08/SC-7")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": {
            "toast-incident-created": toast_visible,
        },
    }))
