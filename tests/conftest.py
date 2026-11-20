"""Shared pytest fixtures."""

import subprocess
import sys


def _ensure_deps():
    try:
        import fastapi  # noqa: F401
        import httpx  # noqa: F401
        import sqlalchemy  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [
                sys.executable, "-m", "pip", "install",
                "fastapi", "uvicorn[standard]", "sqlalchemy",
                "jinja2", "python-multipart", "httpx",
                "-q", "--break-system-packages",
            ]
        )


_ensure_deps()

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def client(engine):
    Session = sessionmaker(bind=engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
