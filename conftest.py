"""Root conftest: ensure dependencies are installed before test collection."""
import subprocess
import sys


def pytest_configure(config):
    """Install required packages if not already available."""
    try:
        import fastapi  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [
                sys.executable, "-m", "pip", "install",
                "fastapi", "uvicorn[standard]", "sqlalchemy",
                "jinja2", "python-multipart", "httpx",
                "-q", "--break-system-packages",
            ]
        )
