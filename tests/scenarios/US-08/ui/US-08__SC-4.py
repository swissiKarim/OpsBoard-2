# scenario-id: US-08/SC-4
"""SC-4: Pressing Escape closes the modal without creating an incident."""
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url.rstrip("/") + "/incidents")
    page.wait_for_selector('[data-testid="btn-new-incident"]')
    page.click('[data-testid="btn-new-incident"]')
    # Wait for modal to open
    page.wait_for_function(
        "document.querySelector('[data-testid=\"modal-new-incident\"]').classList.contains('open')",
        timeout=5000,
    )
    # Press Escape to close
    page.keyboard.press("Escape")
    page.wait_for_function(
        "!document.querySelector('[data-testid=\"modal-new-incident\"]').classList.contains('open')",
        timeout=5000,
    )
    modal_visible = page.is_visible('[data-testid="modal-new-incident"].open')
    screenshot(page, "US-08/SC-4")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": {
            "modal-new-incident": modal_visible,
        },
    }))
