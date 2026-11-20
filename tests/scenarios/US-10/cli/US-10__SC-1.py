# scenario-id: US-10/SC-1
"""SC-1: python -m app.seed creates exactly 6 services and 25 incidents.
then={exit_code equals 0; stdout contains "6"}
"""

import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "app.seed"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}))
