# scenario-id: US-01/SC-3
"""SC-3: pytest suite passes without errors."""

import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "--tb=short"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}))
