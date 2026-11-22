# scenario-id: US-09/SC-8
"""pytest tests cover 404, 422 and 400 cases – run the test suite and report exit code."""
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_error_handling.py", "-q", "--tb=short"],
    capture_output=True,
    text=True,
)
print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
    "stderr": result.stderr[-500:] if len(result.stderr) > 500 else result.stderr,
}))
