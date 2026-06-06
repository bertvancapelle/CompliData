"""Integratie-tests — Koppeling-routes (P5-vervolg, offline guard-patroon)."""
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings

TENANT_A = "11111111-1111-1111-1111-111111111111"
_ID = "22222222-2222-2222-2222-222222222222"
_BRON = "33333333-3333-3333-3333-333333333333"
_DOEL = "44444444-4444-4444-4444-444444444444"

_CREATE_BODY = {
    "bron_applicatie_id": _BRON,
    "doel_applicatie_id": _DOEL,
    "richting": "eenrichting",
    "protocol": "api",
    "impact_bij_verbreking": "hoog",
}


def _fake_koppeling():
    return SimpleNamespace(
        id=uuid.UUID(_ID),
        bron_applicatie_id=uuid.UUID(_BRON),
        doel_applicatie_id=uuid.UUID(_DOEL),
        richting="eenrichting",
        protocol="api",
        impact_bij_verbreking="hoog",
        omschrijving=None,
        created_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
    )


def _maak_app(monkeypatch, payload):
    import app.middleware.auth as auth_mod
    from app.middleware.authz import OnvoldoendeRechten, onvoldoende_rechten_handler
    from app.middleware.tenant import get_tenant_session
    from routes.koppeling import router
    from services import koppeling_service as svc
    from services.errors import (
        KoppelingConflict,
        NietGevonden,
        koppeling_conflict_handler,
        niet_gevonden_handler,
    )

    monkeypatch.setattr(auth_mod, "decode_token", lambda token: payload)

    async def _ok_lijst(*a, **k):
        return ([_fake_koppeling()], None)

    async def _ok_obj(*a, **k):
        return _fake_koppeling()

    async def _ok_none(*a, **k):
        return None

    monkeypatch.setattr(svc, "lijst", _ok_lijst)
    monkeypatch.setattr(svc, "haal_op", _ok_obj)
    monkeypatch.setattr(svc, "maak_aan", _ok_obj)
    monkeypatch.setattr(svc, "werk_bij", _ok_obj)
    monkeypatch.setattr(svc, "verwijder", _ok_none)

    app = FastAPI()
    app.add_exception_handler(OnvoldoendeRechten, onvoldoende_rechten_handler)
    app.add_exception_handler(NietGevonden, niet_gevonden_handler)
    app.add_exception_handler(KoppelingConflict, koppeling_conflict_handler)
    app.include_router(router, prefix="/api/v1")

    async def _fake_session():
        yield SimpleNamespace()

    app.dependency_overrides[get_tenant_session] = _fake_session
    return app, svc


def _client(app, *, met_sessie=True):
    client = TestClient(app)
    if met_sessie:
        client.cookies.set(settings.cookie_name, "dummy")
    return client


def _payload(rol):
    return {"sub": "u-1", "tenant_id": TENANT_A, "realm_access": {"roles": [rol]}}


_ROL_RECHTEN = {
    "viewer": set("L"),
    "medewerker": set("LAW"),
    "beheerder": set("LAWV"),
    "auditor": set("L"),
}

_ENDPOINTS = [
    ("L", "GET", "/api/v1/koppelingen", None, 200),
    ("L", "GET", f"/api/v1/koppelingen/{_ID}", None, 200),
    ("A", "POST", "/api/v1/koppelingen", _CREATE_BODY, 201),
    ("W", "PATCH", f"/api/v1/koppelingen/{_ID}", {"omschrijving": "x"}, 200),
    ("V", "DELETE", f"/api/v1/koppelingen/{_ID}", None, 204),
]


@pytest.mark.parametrize("rol", ["viewer", "medewerker", "beheerder", "auditor"])
@pytest.mark.parametrize("actie,method,pad,body,ok_code", _ENDPOINTS)
def test_rolmatrix(monkeypatch, rol, actie, method, pad, body, ok_code):
    app, _ = _maak_app(monkeypatch, _payload(rol))
    client = _client(app)
    resp = client.request(method, pad, json=body)
    if actie in _ROL_RECHTEN[rol]:
        assert resp.status_code == ok_code, resp.text
    else:
        assert resp.status_code == 403, resp.text
        assert resp.json()["fout"]["code"] == "ONVOLDOENDE_RECHTEN"


def test_geen_sessie_geeft_401(monkeypatch):
    app, _ = _maak_app(monkeypatch, _payload("beheerder"))
    resp = _client(app, met_sessie=False).get("/api/v1/koppelingen")
    assert resp.status_code == 401


def test_bron_gelijk_doel_geeft_422(monkeypatch):
    # Schema-validatie (model_validator) ketst af vóór de handler → FastAPI-422.
    app, _ = _maak_app(monkeypatch, _payload("medewerker"))
    body = {**_CREATE_BODY, "doel_applicatie_id": _BRON}
    resp = _client(app).post("/api/v1/koppelingen", json=body)
    assert resp.status_code == 422


def test_ontbrekende_ouder_geeft_404(monkeypatch):
    app, svc = _maak_app(monkeypatch, _payload("medewerker"))
    from services.errors import NietGevonden

    async def _raise(*a, **k):
        raise NietGevonden("applicatie", _DOEL)

    monkeypatch.setattr(svc, "maak_aan", _raise)
    resp = _client(app).post("/api/v1/koppelingen", json=_CREATE_BODY)
    assert resp.status_code == 404
    assert resp.json()["fout"]["code"] == "NIET_GEVONDEN"


def test_db_backstop_geeft_409(monkeypatch):
    app, svc = _maak_app(monkeypatch, _payload("medewerker"))
    from services.errors import KoppelingConflict

    async def _raise(*a, **k):
        raise KoppelingConflict()

    monkeypatch.setattr(svc, "maak_aan", _raise)
    resp = _client(app).post("/api/v1/koppelingen", json=_CREATE_BODY)
    assert resp.status_code == 409
    assert resp.json()["fout"]["code"] == "KOPPELING_CONFLICT"


def test_kruis_tenant_id_geeft_404(monkeypatch):
    app, svc = _maak_app(monkeypatch, _payload("medewerker"))
    from services.errors import NietGevonden

    async def _raise(*a, **k):
        raise NietGevonden("koppeling", _ID)

    monkeypatch.setattr(svc, "haal_op", _raise)
    resp = _client(app).get(f"/api/v1/koppelingen/{_ID}")
    assert resp.status_code == 404
    assert resp.json()["fout"]["code"] == "NIET_GEVONDEN"


def test_ongeldige_cursor_geeft_400(monkeypatch):
    app, svc = _maak_app(monkeypatch, _payload("viewer"))

    async def _raise(*a, **k):
        raise ValueError("ongeldige cursor")

    monkeypatch.setattr(svc, "lijst", _raise)
    resp = _client(app).get("/api/v1/koppelingen?after=onzin")
    assert resp.status_code == 400
    assert resp.json()["fout"]["code"] == "ONGELDIGE_CURSOR"


def test_lijst_filter_bron_doel_doorgegeven(monkeypatch):
    app, svc = _maak_app(monkeypatch, _payload("viewer"))
    ontvangen = {}

    async def _capture(session, tenant_id, *, limit, after, bron_applicatie_id, doel_applicatie_id):
        ontvangen["bron"] = bron_applicatie_id
        ontvangen["doel"] = doel_applicatie_id
        return ([], None)

    monkeypatch.setattr(svc, "lijst", _capture)
    resp = _client(app).get(
        f"/api/v1/koppelingen?bron_applicatie_id={_BRON}&doel_applicatie_id={_DOEL}"
    )
    assert resp.status_code == 200
    assert str(ontvangen["bron"]) == _BRON
    assert str(ontvangen["doel"]) == _DOEL


def test_ongeldige_uuid_pad_geeft_422(monkeypatch):
    app, _ = _maak_app(monkeypatch, _payload("viewer"))
    resp = _client(app).get("/api/v1/koppelingen/geen-uuid")
    assert resp.status_code == 422
