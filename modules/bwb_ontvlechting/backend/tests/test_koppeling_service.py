"""Unit-tests — Koppeling service-laag (P5-vervolg).

Focus: beide ouders tenant-scoped valideren (bron óf doel ontbreekt → 404),
DB-CHECK-backstop (IntegrityError → KoppelingConflict), tenant-scoped
niet-gevonden. DB gemockt.
"""
import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

_BRON = uuid.uuid4()
_DOEL = uuid.uuid4()


def _create_data(bron=_BRON, doel=_DOEL):
    from schemas.koppeling import KoppelingCreate

    return KoppelingCreate(
        bron_applicatie_id=bron,
        doel_applicatie_id=doel,
        richting="eenrichting",
        protocol="api",
        impact_bij_verbreking="hoog",
    )


def test_maak_aan_doel_buiten_tenant_geeft_nietgevonden(monkeypatch):
    from services import applicatie_service, koppeling_service as svc
    from services.errors import NietGevonden

    async def _haal(session, tenant_id, app_id):
        if str(app_id) == str(_BRON):
            return object()
        raise NietGevonden("applicatie", app_id)  # doel niet in tenant

    monkeypatch.setattr(applicatie_service, "haal_op", _haal)
    session = AsyncMock()

    with pytest.raises(NietGevonden):
        asyncio.run(svc.maak_aan(session, uuid.uuid4(), _create_data()))
    session.commit.assert_not_awaited()


def test_maak_aan_beide_ouders_bestaan(monkeypatch):
    from services import applicatie_service, koppeling_service as svc

    async def _ok(*a, **k):
        return object()

    monkeypatch.setattr(applicatie_service, "haal_op", _ok)
    session = AsyncMock()
    vastgelegd = {}
    session.add = lambda obj: vastgelegd.setdefault("obj", obj)

    tid = "11111111-1111-1111-1111-111111111111"
    obj = asyncio.run(svc.maak_aan(session, tid, _create_data()))

    assert str(obj.bron_applicatie_id) == str(_BRON)
    assert str(obj.doel_applicatie_id) == str(_DOEL)
    assert str(obj.tenant_id) == tid
    session.commit.assert_awaited_once()


def test_maak_aan_integrityerror_geeft_koppelingconflict(monkeypatch):
    from sqlalchemy.exc import IntegrityError

    from services import applicatie_service, koppeling_service as svc
    from services.errors import KoppelingConflict

    async def _ok(*a, **k):
        return object()

    monkeypatch.setattr(applicatie_service, "haal_op", _ok)
    session = AsyncMock()
    session.add = lambda obj: None
    session.commit.side_effect = IntegrityError("stmt", {}, Exception("ck_koppeling"))

    with pytest.raises(KoppelingConflict):
        asyncio.run(svc.maak_aan(session, uuid.uuid4(), _create_data()))
    session.rollback.assert_awaited_once()


def test_haal_op_niet_gevonden():
    from services import koppeling_service as svc
    from services.errors import NietGevonden

    session = AsyncMock()
    resultaat = MagicMock()
    resultaat.scalar_one_or_none.return_value = None
    session.execute.return_value = resultaat

    with pytest.raises(NietGevonden):
        asyncio.run(svc.haal_op(session, uuid.uuid4(), uuid.uuid4()))
