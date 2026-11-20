"""Tests that .gitignore contains required exclusions – covers AC-3."""

import pathlib


def _gitignore_lines() -> list[str]:
    path = pathlib.Path(".gitignore")
    return path.read_text().splitlines()


def test_gitignore_excludes_venv():
    lines = _gitignore_lines()
    assert any(".venv" in line for line in lines), ".venv missing from .gitignore"


def test_gitignore_excludes_pycache():
    lines = _gitignore_lines()
    assert any("__pycache__" in line for line in lines), "__pycache__ missing from .gitignore"


def test_gitignore_excludes_db():
    lines = _gitignore_lines()
    assert any("*.db" in line for line in lines), "*.db missing from .gitignore"


def test_gitignore_excludes_db_wal():
    lines = _gitignore_lines()
    assert any("*.db-wal" in line for line in lines), "*.db-wal missing from .gitignore"


def test_gitignore_excludes_db_shm():
    lines = _gitignore_lines()
    assert any("*.db-shm" in line for line in lines), "*.db-shm missing from .gitignore"
