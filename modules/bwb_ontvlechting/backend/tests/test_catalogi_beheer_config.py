"""Tests — platform-beheer vraagbetekenis- + partijsoort-catalogus (catalogi-beheer-schuld dichten).

Service-laag offline (DB gemockt) + schema-validatie. Enkel-doel catalogi (geen dimensie),
soft-deactivate (geen V). Spiegelt het relatiekenmerk/contractconfig-patroon.
"""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError


def _result(val):
    r = MagicMock()
    r.scalar_one_or_none.return_value = val
    return r


def _scalar_one(val):
    r = MagicMock()
    r.scalar_one.return_value = val
    return r


def _optie(id=1, optie_sleutel="leverancier", label="Leverancier", volgorde=0, actief=True):
    return SimpleNamespace(id=id, optie_sleutel=optie_sleutel, label=label, volgorde=volgorde, actief=actief)


# ── Schemas (beide catalogi gelijk) ──────────────────────────────────────────────
@pytest.mark.parametrize("mod", ["vraagbetekenisconfig", "partijsoortconfig"])
def test_schema_patroon_en_immutability(mod):
    import importlib

    m = importlib.import_module(f"schemas.{mod}")
    Create = getattr(m, [n for n in dir(m) if n.endswith("OptieCreate")][0])
    Update = getattr(m, [n for n in dir(m) if n.endswith("OptieUpdate")][0])

    ok = Create(optie_sleutel="ketenpartner", label="Ketenpartner")
    assert ok.optie_sleutel == "ketenpartner" and ok.volgorde is None
    for slecht in ("Hoofdletter", "met spatie", "1leading"):
        with pytest.raises(ValidationError):
            Create(optie_sleutel=slecht, label="X")
    assert Update(actief=False).actief is False
    with pytest.raises(ValidationError):  # optie_sleutel immutable (niet in Update)
        Update(optie_sleutel="x")


# ── Service: voeg_toe / wijzig (beide catalogi) ──────────────────────────────────
def _svc_en_create(mod):
    import importlib

    svc = importlib.import_module(f"services.{mod}_service")
    schemas = importlib.import_module(f"schemas.{mod}")
    Create = getattr(schemas, [n for n in dir(schemas) if n.endswith("OptieCreate")][0])
    Update = getattr(schemas, [n for n in dir(schemas) if n.endswith("OptieUpdate")][0])
    return svc, Create, Update


@pytest.mark.parametrize("mod", ["vraagbetekenisconfig", "partijsoortconfig"])
def test_voeg_toe_happy_en_volgorde_achteraan(mod):
    svc, Create, _ = _svc_en_create(mod)
    session = AsyncMock()
    session.execute.side_effect = [_result(None), _scalar_one(4)]  # geen duplicaat, max(volgorde)=4
    session.add = lambda o: None
    asyncio.run(svc.voeg_toe(session, Create(optie_sleutel="nieuw", label="Nieuw")))
    session.commit.assert_awaited()


@pytest.mark.parametrize("mod", ["vraagbetekenisconfig", "partijsoortconfig"])
def test_voeg_toe_duplicaat_409(mod):
    from services.errors import ConfiguratieConflict

    svc, Create, _ = _svc_en_create(mod)
    session = AsyncMock()
    session.execute.side_effect = [_result(7)]  # sleutel bestaat al
    with pytest.raises(ConfiguratieConflict):
        asyncio.run(svc.voeg_toe(session, Create(optie_sleutel="bestaat", label="X")))


@pytest.mark.parametrize("mod", ["vraagbetekenisconfig", "partijsoortconfig"])
def test_wijzig_soft_deactivate(mod):
    svc, _, Update = _svc_en_create(mod)
    obj = _optie(actief=True)
    session = AsyncMock()
    session.execute.side_effect = [_result(obj)]  # _haal
    asyncio.run(svc.wijzig(session, 1, Update(actief=False)))
    assert obj.actief is False  # soft-deactivate (geen hard delete)
    session.commit.assert_awaited()


@pytest.mark.parametrize("mod", ["vraagbetekenisconfig", "partijsoortconfig"])
def test_wijzig_onbekend_id_404(mod):
    from services.errors import NietGevonden

    svc, _, Update = _svc_en_create(mod)
    session = AsyncMock()
    session.execute.side_effect = [_result(None)]
    with pytest.raises(NietGevonden):
        asyncio.run(svc.wijzig(session, 999, Update(label="X")))


# ── RBAC: nieuwe platform-entiteiten, geen V ─────────────────────────────────────
def test_nieuwe_platform_entiteiten_geen_verwijderen():
    from app.core.platform_rbac import Actie, PlatformEntiteit, heeft_platform_permissie

    for ent in (PlatformEntiteit.VRAAGBETEKENISCONFIG, PlatformEntiteit.PARTIJSOORTCONFIG):
        assert heeft_platform_permissie(["platformbeheerder"], ent, Actie.WIJZIGEN)
        assert heeft_platform_permissie(["platformoperator"], ent, Actie.LEZEN)
        assert not heeft_platform_permissie(["platformoperator"], ent, Actie.WIJZIGEN)
        for rol in ("platformbeheerder", "platformoperator"):
            assert not heeft_platform_permissie([rol], ent, Actie.VERWIJDEREN)
