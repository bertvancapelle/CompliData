"""Tests — opties-endpoints voor Checklistscore en Blokkade (read-only enums)."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings

TENANT_A = "11111111-1111-1111-1111-111111111111"


def _maak_app(monkeypatch, router, payload):
    import app.middleware.auth as auth_mod
    from app.middleware.authz import OnvoldoendeRechten, onvoldoende_rechten_handler

    monkeypatch.setattr(auth_mod, "decode_token", lambda token: payload)
    app = FastAPI()
    app.add_exception_handler(OnvoldoendeRechten, onvoldoende_rechten_handler)
    app.include_router(router, prefix="/api/v1")
    return app


def _payload(rol):
    return {"sub": "u-1", "tenant_id": TENANT_A, "realm_access": {"roles": [rol]}}


def test_checklistscore_enum_opties():
    from models.models import ChecklistScore
    from services.checklistscore_service import enum_opties

    assert enum_opties() == {"score": [e.value for e in ChecklistScore]}
    assert enum_opties()["score"] == ["ja", "deels", "nee", "nvt"]


def test_blokkade_enum_opties():
    from models.models import BlokkadeStatus
    from services.blokkade_service import enum_opties

    assert enum_opties() == {"status": [e.value for e in BlokkadeStatus]}
    assert enum_opties()["status"] == ["open", "in_behandeling", "opgelost"]


def test_checklistscore_opties_route_viewer_ok(monkeypatch):
    from routes.checklistscore import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("viewer")))
    client.cookies.set(settings.cookie_name, "dummy")
    resp = client.get("/api/v1/checklistscores/opties")
    assert resp.status_code == 200, resp.text
    assert set(resp.json().keys()) == {"score"}


def test_blokkade_opties_route_viewer_ok(monkeypatch):
    from routes.blokkade import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("viewer")))
    client.cookies.set(settings.cookie_name, "dummy")
    resp = client.get("/api/v1/blokkades/opties")
    assert resp.status_code == 200, resp.text
    assert set(resp.json().keys()) == {"status"}


def test_opties_vereist_auth(monkeypatch):
    from routes.checklistscore import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("viewer")))  # geen cookie
    assert client.get("/api/v1/checklistscores/opties").status_code == 401


def test_opties_pad_niet_als_uuid_geparsed(monkeypatch):
    from routes.blokkade import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("beheerder")))
    client.cookies.set(settings.cookie_name, "dummy")
    assert client.get("/api/v1/blokkades/opties").status_code == 200
