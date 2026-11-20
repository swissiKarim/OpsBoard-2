"""Tests for the /health endpoint – covers AC-1 and AC-2."""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_body(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_app_is_fastapi(client):
    from fastapi import FastAPI

    from app.main import app as fastapi_app

    assert isinstance(fastapi_app, FastAPI)
