# scenario-id: US-01/SC-4
"""SC-4: .gitignore excludes .venv, __pycache__, *.db, *.db-wal, *.db-shm."""

import json
import pathlib

content = pathlib.Path(".gitignore").read_text()

print(json.dumps({"stdout": content}))
