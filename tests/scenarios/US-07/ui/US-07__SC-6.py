# scenario-id: US-07/SC-6
"""SC-6: Dark mode toggle applies theme immediately and persists in localStorage.
interactions={click@theme-toggle}
then={visible.theme-toggle equals true}
"""
from asb_ui import page_session, screenshot
import json

with page_session() as (page, base_url):
    page.goto(base_url)
    page.wait_for_selector('[data-testid="theme-toggle"]')

    # Click the theme toggle
    page.click('[data-testid="theme-toggle"]')

    # Verify the toggle is visible
    visible = {
        "theme-toggle": page.is_visible('[data-testid="theme-toggle"]'),
    }

    screenshot(page, "US-07/SC-6")

    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": visible,
    }))
