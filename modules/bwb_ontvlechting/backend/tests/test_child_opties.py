"""Tests — opties-endpoints voor Datatype en Koppeling (read-only enum-metadata).

Gebruikersgroep heeft géén enum-velden (organisatie = vrije tekst) en dus geen
opties-endpoint — bewust niet getest.
"""
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


# ── Pure helpers (single source) ────────────────────────────────────────────

def test_datatype_enum_opties():
    from models.models import DatatypeCategorie
    from services.datatype_service import enum_opties

    assert enum_opties() == {"categorie": [e.value for e in DatatypeCategorie]}
    assert "combinatie" in enum_opties()["categorie"]  # code = 6 waarden


def test_koppeling_enum_opties():
    from models.models import ImpactVerbreking, Koppelprotocol, Koppelrichting
    from services.koppeling_service import enum_opties

    o = enum_opties()
    assert o["richting"] == [e.value for e in Koppelrichting]
    assert o["protocol"] == [e.value for e in Koppelprotocol]
    assert o["impact_bij_verbreking"] == [e.value for e in ImpactVerbreking]
    assert "bron_applicatie_id" not in o and "doel_applicatie_id" not in o


# ── Routes: auth-gate + route-volgorde ──────────────────────────────────────

def test_datatype_opties_route_viewer_ok(monkeypatch):
    from routes.datatype import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("viewer")))
    client.cookies.set(settings.cookie_name, "dummy")
    resp = client.get("/api/v1/datatypes/opties")
    assert resp.status_code == 200, resp.text
    assert set(resp.json().keys()) == {"categorie"}


def test_koppeling_opties_route_viewer_ok(monkeypatch):
    from routes.koppeling import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("viewer")))
    client.cookies.set(settings.cookie_name, "dummy")
    resp = client.get("/api/v1/koppelingen/opties")
    assert resp.status_code == 200, resp.text
    assert set(resp.json().keys()) == {"richting", "protocol", "impact_bij_verbreking"}


def test_opties_vereist_auth(monkeypatch):
    from routes.datatype import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("viewer")))  # geen cookie
    assert client.get("/api/v1/datatypes/opties").status_code == 401


def test_opties_pad_niet_als_uuid_geparsed(monkeypatch):
    # Route-volgorde: 'opties' raakt niet de /{id}-route (zou 422 geven).
    from routes.koppeling import router

    client = TestClient(_maak_app(monkeypatch, router, _payload("beheerder")))
    client.cookies.set(settings.cookie_name, "dummy")
    assert client.get("/api/v1/koppelingen/opties").status_code == 200
