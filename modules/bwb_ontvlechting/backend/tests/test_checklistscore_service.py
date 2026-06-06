"""Unit-tests — Checklistscore service-laag (ADR-013, Model A).

Focus: ouder-/vraag_code-validatie, uniciteit, de auto-blokkade-invariant
(`_synchroniseer_blokkade`) en dat een schrijf de lifecycle-herberekening
aanroept. DB gemockt.
"""
import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

_APP = uuid.uuid4()


def _create(score="nee", vraag="1.1"):
    from schemas.checklistscore import ChecklistscoreCreate

    return ChecklistscoreCreate(applicatie_id=_APP, vraag_code=vraag, score=score)


def _result(waarde):
    r = MagicMock()
    r.scalar_one_or_none.return_value = waarde
    return r


# ── maak_aan: validatie-paden ───────────────────────────────────────────────

def test_maak_aan_ouder_ontbreekt(monkeypatch):
    from services import applicatie_service, checklistscore_service as svc
    from services.errors import NietGevonden

    async def _raise(*a, **k):
        raise NietGevonden("applicatie", "x")

    monkeypatch.setattr(applicatie_service, "haal_op", _raise)
    with pytest.raises(NietGevonden):
        asyncio.run(svc.maak_aan(AsyncMock(), uuid.uuid4(), _create()))


def test_maak_aan_onbekende_vraag_code(monkeypatch):
    from services import applicatie_service, checklistscore_service as svc
    from services.errors import NietGevonden

    async def _ok(*a, **k):
        return object()

    monkeypatch.setattr(applicatie_service, "haal_op", _ok)
    session = AsyncMock()
    session.execute.side_effect = [_result(None)]  # vraag_code niet gevonden
    with pytest.raises(NietGevonden):
        asyncio.run(svc.maak_aan(session, uuid.uuid4(), _create()))


def test_maak_aan_dubbele_score(monkeypatch):
    from services import applicatie_service, checklistscore_service as svc
    from services.errors import ChecklistscoreConflict

    async def _ok(*a, **k):
        return object()

    monkeypatch.setattr(applicatie_service, "haal_op", _ok)
    session = AsyncMock()
    session.execute.side_effect = [
        _result("1.1"),          # vraag_code bestaat
        _result(uuid.uuid4()),   # bestaande score gevonden → conflict
    ]
    with pytest.raises(ChecklistscoreConflict):
        asyncio.run(svc.maak_aan(session, uuid.uuid4(), _create()))


def test_maak_aan_roept_herbereken(monkeypatch):
    from services import applicatie_service, checklistscore_service as svc, lifecycle_service

    async def _ok(*a, **k):
        return object()

    monkeypatch.setattr(applicatie_service, "haal_op", _ok)
    aangeroepen = {}

    async def _herb(session, tenant_id, app_id):
        aangeroepen["yes"] = True

    monkeypatch.setattr(lifecycle_service, "herbereken_lifecycle", _herb)

    session = AsyncMock()
    session.add = lambda o: None
    # vraag bestaat, geen dup, geen bestaande blokkade (score nvt → geen blokkade)
    session.execute.side_effect = [_result("1.1"), _result(None), _result(None)]
    asyncio.run(svc.maak_aan(session, uuid.uuid4(), _create(score="nvt")))
    assert aangeroepen.get("yes") is True


# ── invariant score↔blokkade (_synchroniseer_blokkade) ──────────────────────

def test_aanmaken_score_nee_maakt_blokkade_open():
    # oude_score=None ⇒ aanmaken met blokkerende score
    from models.models import BlokkadeStatus, ChecklistScore
    from services.checklistscore_service import _synchroniseer_blokkade

    score_obj = SimpleNamespace(id=uuid.uuid4(), applicatie_id=_APP, score=ChecklistScore.nee)
    session = AsyncMock()
    session.execute.return_value = _result(None)  # nog geen blokkade
    toegevoegd = []
    session.add = lambda o: toegevoegd.append(o)

    asyncio.run(_synchroniseer_blokkade(session, uuid.uuid4(), score_obj, oude_score=None))

    assert len(toegevoegd) == 1
    assert toegevoegd[0].status == BlokkadeStatus.open


def test_transitie_nee_naar_ja_lost_actieve_blokkade_op():
    from models.models import BlokkadeStatus, ChecklistScore
    from services.checklistscore_service import _synchroniseer_blokkade

    blok = SimpleNamespace(status=BlokkadeStatus.open, opgelost_op=None)
    score_obj = SimpleNamespace(id=uuid.uuid4(), applicatie_id=_APP, score=ChecklistScore.ja)
    session = AsyncMock()
    session.execute.return_value = _result(blok)

    asyncio.run(_synchroniseer_blokkade(session, uuid.uuid4(), score_obj, ChecklistScore.nee))

    assert blok.status == BlokkadeStatus.opgelost
    assert blok.opgelost_op is not None


def test_transitie_ja_naar_nee_heropent_opgeloste_blokkade():
    # Echte regressie: ja → nee (de uitgangsscore was NIET blokkerend)
    from models.models import BlokkadeStatus, ChecklistScore
    from services.checklistscore_service import _synchroniseer_blokkade

    blok = SimpleNamespace(status=BlokkadeStatus.opgelost, opgelost_op="2026-01-01")
    score_obj = SimpleNamespace(id=uuid.uuid4(), applicatie_id=_APP, score=ChecklistScore.nee)
    session = AsyncMock()
    session.execute.return_value = _result(blok)

    asyncio.run(_synchroniseer_blokkade(session, uuid.uuid4(), score_obj, ChecklistScore.ja))

    assert blok.status == BlokkadeStatus.open
    assert blok.opgelost_op is None


def test_ongewijzigde_nee_score_laat_opgeloste_blokkade_met_rust():
    # Kern van de correctie: nee → nee (bv. alleen bevinding gewijzigd) mag een
    # geremedieerde (opgeloste) blokkade NIET heropenen → migratieklaar blijft.
    from models.models import BlokkadeStatus, ChecklistScore
    from services.checklistscore_service import _synchroniseer_blokkade

    blok = SimpleNamespace(status=BlokkadeStatus.opgelost, opgelost_op="2026-01-01")
    score_obj = SimpleNamespace(id=uuid.uuid4(), applicatie_id=_APP, score=ChecklistScore.nee)
    session = AsyncMock()
    session.execute.return_value = _result(blok)

    asyncio.run(_synchroniseer_blokkade(session, uuid.uuid4(), score_obj, ChecklistScore.nee))

    assert blok.status == BlokkadeStatus.opgelost  # niet heropend
    assert blok.opgelost_op == "2026-01-01"


def test_binnen_blokkerend_nee_naar_deels_laat_blokkade_met_rust():
    from models.models import BlokkadeStatus, ChecklistScore
    from services.checklistscore_service import _synchroniseer_blokkade

    blok = SimpleNamespace(status=BlokkadeStatus.in_behandeling, opgelost_op=None)
    score_obj = SimpleNamespace(id=uuid.uuid4(), applicatie_id=_APP, score=ChecklistScore.deels)
    session = AsyncMock()
    session.execute.return_value = _result(blok)

    asyncio.run(_synchroniseer_blokkade(session, uuid.uuid4(), score_obj, ChecklistScore.nee))

    assert blok.status == BlokkadeStatus.in_behandeling  # ongemoeid


def test_haal_op_niet_gevonden():
    from services import checklistscore_service as svc
    from services.errors import NietGevonden

    session = AsyncMock()
    session.execute.return_value = _result(None)
    with pytest.raises(NietGevonden):
        asyncio.run(svc.haal_op(session, uuid.uuid4(), uuid.uuid4()))
