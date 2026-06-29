"""Tests — registratiegaten_service (ADR-035 Slice 1). Offline (gemockte session).

Borgt de engine-invariant (geen engine-symbolen geïmporteerd) + de badge-signaalmatrix +
de mapping van de lijst-functies. Geen DB nodig (asyncio.run + AsyncMock)."""
import asyncio
import uuid
from unittest.mock import AsyncMock, Mock

from services import registratiegaten_service as svc

TID = str(uuid.uuid4())


def _res_first(val):
    r = Mock()
    r.first = Mock(return_value=val)
    return r


def _res_all(rows):
    r = Mock()
    r.all = Mock(return_value=rows)
    return r


def _row(naam="X", lc=None, _id=None):
    return Mock(id=_id or uuid.uuid4(), naam=naam, lifecycle_status=lc)


def test_registratiegaten_engine_afwezigheid():
    """Engine-invariant: geen schrijf-/engine-symbolen in de servicemodule."""
    for naam in ["lifecycle_service", "herbereken_lifecycle", "bepaal_lifecycle",
                 "ComponentProfiel", "Blokkade", "Checklistscore"]:
        assert not hasattr(svc, naam), f"verboden engine-symbool aanwezig: {naam}"


def test_badge_component_geen_gaten():
    """Component MET eigenaar én MET rol → geen signalen."""
    s = AsyncMock()
    # 1) bestaat → row; 2) geen-eigenaar-query → None; 3) rol-query → row (rol bestaat)
    s.execute = AsyncMock(side_effect=[_res_first(("c",)), _res_first(None), _res_first(("rol",))])
    out = asyncio.run(svc.badge_voor_component(s, TID, uuid.uuid4()))
    assert out == {"signalen": [], "kritiek": 0, "aandacht": 0}


def test_badge_component_beide_gaten():
    """Component ZONDER eigenaar én ZONDER rol → twee kritieke signalen."""
    s = AsyncMock()
    s.execute = AsyncMock(side_effect=[_res_first(("c",)), _res_first(("c",)), _res_first(None)])
    out = asyncio.run(svc.badge_voor_component(s, TID, uuid.uuid4()))
    assert out["kritiek"] == 2 and out["aandacht"] == 0
    assert set(out["signalen"]) == {"component_zonder_eigenaar", "component_zonder_verantwoordelijke"}


def test_badge_component_alleen_eigenaar_ontbreekt():
    """ZONDER eigenaar maar MET rol → één signaal."""
    s = AsyncMock()
    s.execute = AsyncMock(side_effect=[_res_first(("c",)), _res_first(("c",)), _res_first(("rol",))])
    out = asyncio.run(svc.badge_voor_component(s, TID, uuid.uuid4()))
    assert out["signalen"] == ["component_zonder_eigenaar"] and out["kritiek"] == 1


def test_badge_component_onbestaand_leeg():
    """Onbestaand/kruis-tenant component → lege badge (geen lek), één execute."""
    s = AsyncMock()
    s.execute = AsyncMock(side_effect=[_res_first(None)])
    out = asyncio.run(svc.badge_voor_component(s, TID, uuid.uuid4()))
    assert out == {"signalen": [], "kritiek": 0, "aandacht": 0}


def test_component_zonder_eigenaar_mapping():
    """Lijst-functie mapt rijen naar het signaal-dict (kritiek)."""
    s = AsyncMock()
    s.execute = AsyncMock(return_value=_res_all([_row("Zaaksysteem", "concept"), _row("BRP", None)]))
    out = asyncio.run(svc.component_zonder_eigenaar(s, TID))
    assert len(out) == 2
    assert out[0]["naam"] == "Zaaksysteem" and out[0]["lifecycle_status"] == "concept"
    assert out[0]["signaal"] == "component_zonder_eigenaar" and out[0]["niveau"] == "kritiek"
    assert out[1]["lifecycle_status"] is None


def test_component_zonder_verantwoordelijke_mapping():
    s = AsyncMock()
    s.execute = AsyncMock(return_value=_res_all([_row("DMS", "in_inventarisatie")]))
    out = asyncio.run(svc.component_zonder_verantwoordelijke(s, TID))
    assert out[0]["signaal"] == "component_zonder_verantwoordelijke" and out[0]["niveau"] == "kritiek"
