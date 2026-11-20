"""Shared Jinja2Templates instance for OpsBoard.

Import this everywhere instead of constructing a new Jinja2Templates()
per router – multiple instances cause a dict-hashability bug in
Starlette's LRUCache when the same template is loaded from different
instances sharing the same environment cache key.
"""

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
