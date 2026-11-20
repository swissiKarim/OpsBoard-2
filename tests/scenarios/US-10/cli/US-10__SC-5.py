# scenario-id: US-10/SC-5
"""SC-5: Seed command is idempotent – running it twice exits 0 both times.
then={exit_code equals 0}
"""

import json
import subprocess
import sys

# Run seed a second time to verify idempotency
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
