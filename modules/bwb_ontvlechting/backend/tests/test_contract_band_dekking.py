"""Tests — ADR-030 per-band dekking. De toon_per_band-/label-logica is puur getest (`_bouw_respons`);
de validatie (422) offline via een gemockte sessie. De SQL-upsert/-delete + WHERE-correctheid zijn de
offline-grens (live-DB)."""
import asyncio
import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from services import contract_band_dekking_service as svc
from services.errors import OngeldigeRegistratie

TID = str(uuid.uuid4())
LBL = {"hosting": ("Hosting", True), "onderhoud": ("Onderhoud", True), "licentie": ("Licentie", True)}


def test_geen_band_dekking_toon_false():
    r = svc._bouw_respons(["hosting", "onderhoud"], None, LBL)
    assert r["per_band"] is None
    assert r["per_band_sleutels"] is None
    assert r["toon_per_band"] is False
    assert r["contract_breed"] == ["Hosting", "Onderhoud"]


def test_band_gelijk_aan_contract_breed_toon_false():
    # zelfde set (andere volgorde) → geen herhaling tonen
    r = svc._bouw_respons(["hosting", "onderhoud"], ["onderhoud", "hosting"], LBL)
    assert r["toon_per_band"] is False
    assert r["per_band"] == ["Onderhoud", "Hosting"]


def test_band_afwijkend_toon_true():
    r = svc._bouw_respons(["hosting", "onderhoud"], ["hosting", "licentie"], LBL)
    assert r["toon_per_band"] is True
    assert r["per_band"] == ["Hosting", "Licentie"]
    assert r["per_band_sleutels"] == ["hosting", "licentie"]


def test_onbekende_sleutel_valt_terug_op_zichzelf():
    r = svc._bouw_respons(["xyz"], None, LBL)
    assert r["contract_breed"] == ["xyz"]  # fallback: label = sleutel


def test_stel_band_dekking_in_weigert_ongeldige_sleutel(monkeypatch):
    """Contract + component bestaan, maar een onbekende dekking-sleutel ⇒ 422 ONGELDIGE_OPTIE."""
    s = AsyncMock()
    res = Mock()
    res.first = Mock(return_value=("bestaat",))  # _bestaat: contract én component gevonden
    s.execute = AsyncMock(return_value=res)
    monkeypatch.setattr(svc.catalog, "actieve_sleutels", AsyncMock(return_value={"hosting", "onderhoud"}))
    with pytest.raises(OngeldigeRegistratie):
        asyncio.run(svc.stel_band_dekking_in(s, TID, uuid.uuid4(), uuid.uuid4(), ["onbekend"]))
