# scenario-id: US-02/SC-5
"""SC-5: Unit tests cover all three status outcomes including SEV1 resolution transition.
Runs pytest on the status engine unit test file and reports exit code.
"""

import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_status_engine.py", "-q", "--tb=short"],
    capture_output=True,
    text=True,
)

print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout[-2000:] if result.stdout else "",
    "stderr": result.stderr[-500:] if result.stderr else "",
}))
