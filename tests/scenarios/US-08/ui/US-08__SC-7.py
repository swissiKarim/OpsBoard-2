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
    # Service and severity already have default selections
    page.click('[data-testid="modal-incident-service"]')
    page.keyboard.press("Escape")
    page.click('[data-testid="modal-incident-severity"]')
    page.keyboard.press("Escape")
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
