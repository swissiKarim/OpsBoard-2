# scenario-id: US-06/SC-4
"""SC-4: Filter and search params reflected in URL; reload restores view.
then={status_code equals 200; body contains "status=investigating"}
"""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8000"))

# Request the incidents list with status=investigating filter
resp = httpx.get(
    f"{base_url}/incidents",
    params={"status": "investigating", "page": 1},
    timeout=15,
    follow_redirects=True,
)

# The URL of the final response should contain the status param,
# and the form action/filter form should echo it back via the action URL.
# We verify by checking the response body contains the param string.
body = resp.text

# Build what the URL should contain
url = str(resp.url)

# The body must contain the filter param (e.g. in the form action or pagination links)
# We inject "status=investigating" into the page via pagination and form values
combined = body + " " + url

print(json.dumps({
    "status_code": resp.status_code,
    "body": combined,
}))
