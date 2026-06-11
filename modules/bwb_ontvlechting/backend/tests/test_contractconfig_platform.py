"""Tests — platform-beheer contractcatalogus (ADR-020 fase C / Addendum B, CD042).

Service-laag offline (DB gemockt) + guard/RBAC-integratie via een test-app.
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import settings


def _result(val):
    r = MagicMock()
    r.scalar_one_or_none.return_value = val
    return r


def _scalar_one(val):
    r = MagicMock()
    r.scalar_one.return_value = val
    return r


def _scalars(rows):
    r = MagicMock()
    r.scalars.return_value.all.return_value = rows
    return r


async def _async(val):
    return val


def _optie(id=1, dimensie=None, optie_sleutel="hosting", label="Hosting", volgorde=0, actief=True):
    from models.models import ContractConfigDimensie
    return SimpleNamespace(
        id=id, dimensie=dimensie or ContractConfigDimensie.dekking,
        optie_sleutel=optie_sleutel, label=label, volgorde=volgorde, actief=actief,
    )


# ── Schemas ─────────────────────────────────────────────────────────────────────

def test_create_sleutel_patroon_en_immutability():
    from schemas.contractconfig import ContractConfigOptieCreate, ContractConfigOptieUpdate

    ok = ContractConfigOptieCreate(dimensie="dekking", optie_sleutel="nieuw_model", label="Nieuw")
    assert ok.optie_sleutel == "nieuw_model" and ok.volgorde is None

    # Sleutel-patroon: geen hoofdletters/spaties/leidend cijfer
    for slecht in ("Hoofdletter", "met spatie", "1leading"):
        with pytest.raises(ValidationError):
            ContractConfigOptieCreate(dimensie="dekking", optie_sleutel=slecht, label="X")
    with pytest.raises(ValidationError):
        ContractConfigOptieCreate(dimensie="onzin", optie_sleutel="x", label="X")  # enum

    # Update: dimensie/optie_sleutel immutable ⇒ extra='forbid' ⇒ 422
    assert ContractConfigOptieUpdate(actief=False).actief is False
    with pytest.raises(ValidationError):
        ContractConfigOptieUpdate(dimensie="dekking")
    with pytest.raises(ValidationError):
        ContractConfigOptieUpdate(optie_sleutel="x")


# ── Service ─────────────────────────────────────────────────────────────────────

def test_voeg_toe_default_volgorde_max_plus_1():
    from schemas.contractconfig import ContractConfigOptieCreate
    from services import contractconfig_service as svc

    session = AsyncMock()
    # dup-check → None ; max(volgorde) → 2
    session.execute.side_effect = [_result(None), _scalar_one(2)]
    toegevoegd = []
    session.add = lambda o: toegevoegd.append(o)

    asyncio.run(svc.voeg_toe(session, ContractConfigOptieCreate(
        dimensie="dekking", optie_sleutel="extra", label="Extra")))
    assert len(toegevoegd) == 1
    assert toegevoegd[0].volgorde == 3  # max+1
    assert toegevoegd[0].actief is True
    session.commit.assert_awaited_once()


def test_voeg_toe_expliciete_volgorde():
    from schemas.contractconfig import ContractConfigOptieCreate
    from services import contractconfig_service as svc

    session = AsyncMock()
    session.execute.side_effect = [_result(None)]  # alleen dup-check; geen max-query
    toegevoegd = []
    session.add = lambda o: toegevoegd.append(o)

    asyncio.run(svc.voeg_toe(session, ContractConfigOptieCreate(
        dimensie="kostenmodel", optie_sleutel="staffel", label="Staffel", volgorde=7)))
    assert toegevoegd[0].volgorde == 7


def test_voeg_toe_duplicaat_geeft_conflict():
    from schemas.contractconfig import ContractConfigOptieCreate
    from services import contractconfig_service as svc
    from services.errors import ConfiguratieConflict

    session = AsyncMock()
    session.execute.return_value = _result(99)  # bestaat al
    with pytest.raises(ConfiguratieConflict):
        asyncio.run(svc.voeg_toe(session, ContractConfigOptieCreate(
            dimensie="dekking", optie_sleutel="hosting", label="Hosting")))
    session.commit.assert_not_awaited()


def test_wijzig_onbekend_id_404():
    from schemas.contractconfig import ContractConfigOptieUpdate
    from services import contractconfig_service as svc
    from services.errors import NietGevonden

    session = AsyncMock()
    session.execute.return_value = _result(None)
    with pytest.raises(NietGevonden):
        asyncio.run(svc.wijzig(session, 123, ContractConfigOptieUpdate(label="X")))


def test_wijzig_deactiveren_en_reactiveren():
    from schemas.contractconfig import ContractConfigOptieUpdate
    from services import contractconfig_service as svc

    optie = _optie(actief=True)
    session = AsyncMock()
    session.execute.return_value = _result(optie)
    asyncio.run(svc.wijzig(session, optie.id, ContractConfigOptieUpdate(actief=False)))
    assert optie.actief is False  # soft-deactivate, altijd toegestaan

    optie2 = _optie(actief=False)
    session.execute.return_value = _result(optie2)
    asyncio.run(svc.wijzig(session, optie2.id, ContractConfigOptieUpdate(actief=True, label="Herstel")))
    assert optie2.actief is True and optie2.label == "Herstel"


def test_lijst_geeft_rijen_terug():
    from services import contractconfig_service as svc

    session = AsyncMock()
    session.execute.return_value = _scalars([_optie(), _optie(id=2, optie_sleutel="licentie_aanschaf")])
    rijen = asyncio.run(svc.lijst(session))
    assert len(rijen) == 2


# ── Guard / RBAC-integratie ─────────────────────────────────────────────────────

def _app(monkeypatch, payload):
    import app.middleware.auth as auth_mod
    from app.middleware.authz import OnvoldoendeRechten, onvoldoende_rechten_handler
    from app.middleware.tenant import get_platform_session
    from routes.contractconfig import router
    from services import contractconfig_service as svc

    monkeypatch.setattr(auth_mod, "decode_token", lambda token: payload)
    app = FastAPI()
    app.add_exception_handler(OnvoldoendeRechten, onvoldoende_rechten_handler)
    app.include_router(router, prefix="/api/v1")

    async def _fake_session():
        yield SimpleNamespace()

    app.dependency_overrides[get_platform_session] = _fake_session
    monkeypatch.setattr(svc, "lijst", lambda *_a, **_k: _async([]))
    return app


_PB = {"sub": "pb", "realm_access": {"roles": ["platformbeheerder"]}}
_PO = {"sub": "po", "realm_access": {"roles": ["platformoperator"]}}
_TENANT = {"sub": "tb", "tenant_id": "t1", "realm_access": {"roles": ["beheerder"]}}


def _client(monkeypatch, payload):
    c = TestClient(_app(monkeypatch, payload))
    c.cookies.set(settings.cookie_name, "tok")
    return c


def test_401_zonder_sessie(monkeypatch):
    c = TestClient(_app(monkeypatch, _PB))  # geen cookie
    assert c.get("/api/v1/platform/contractconfig").status_code == 401


def test_403_voor_tenantrol(monkeypatch):
    r = _client(monkeypatch, _TENANT).get("/api/v1/platform/contractconfig")
    assert r.status_code == 403
    assert r.json()["fout"]["code"] == "ONVOLDOENDE_RECHTEN"


def test_operator_leest_wel(monkeypatch):
    assert _client(monkeypatch, _PO).get("/api/v1/platform/contractconfig").status_code == 200


def test_operator_mag_niet_toevoegen(monkeypatch):
    r = _client(monkeypatch, _PO).post(
        "/api/v1/platform/contractconfig",
        json={"dimensie": "dekking", "optie_sleutel": "x", "label": "X"},
    )
    assert r.status_code == 403


def test_operator_mag_niet_wijzigen(monkeypatch):
    r = _client(monkeypatch, _PO).patch("/api/v1/platform/contractconfig/1", json={"actief": False})
    assert r.status_code == 403


def test_beheerder_mag_toevoegen(monkeypatch):
    from services import contractconfig_service as svc

    monkeypatch.setattr(svc, "voeg_toe", lambda *_a, **_k: _async(_optie(optie_sleutel="extra", label="Extra")))
    r = _client(monkeypatch, _PB).post(
        "/api/v1/platform/contractconfig",
        json={"dimensie": "dekking", "optie_sleutel": "extra", "label": "Extra"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["optie_sleutel"] == "extra"
