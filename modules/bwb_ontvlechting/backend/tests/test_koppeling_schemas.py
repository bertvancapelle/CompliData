"""Unit-tests — Koppeling-schemas (P5-vervolg)."""
import uuid

import pytest
from pydantic import ValidationError


def _basis() -> dict:
    return {
        "bron_applicatie_id": str(uuid.uuid4()),
        "doel_applicatie_id": str(uuid.uuid4()),
        "richting": "eenrichting",
        "protocol": "api",
        "impact_bij_verbreking": "hoog",
    }


def test_create_happy_path():
    from schemas.koppeling import KoppelingCreate

    m = KoppelingCreate(**_basis())
    assert m.richting.value == "eenrichting"
    assert m.protocol.value == "api"
    assert m.impact_bij_verbreking.value == "hoog"


def test_create_extra_forbid():
    from schemas.koppeling import KoppelingCreate

    with pytest.raises(ValidationError):
        KoppelingCreate(**_basis(), onbekend="x")


def test_create_bron_gelijk_doel_geweigerd():
    from schemas.koppeling import KoppelingCreate

    zelfde = str(uuid.uuid4())
    d = _basis()
    d["bron_applicatie_id"] = zelfde
    d["doel_applicatie_id"] = zelfde
    with pytest.raises(ValidationError):
        KoppelingCreate(**d)


def test_create_ongeldig_protocol():
    from schemas.koppeling import KoppelingCreate

    d = _basis()
    d["protocol"] = "carrier-pigeon"
    with pytest.raises(ValidationError):
        KoppelingCreate(**d)


def test_create_alle_protocollen_en_impact():
    from models.models import ImpactVerbreking, Koppelprotocol
    from schemas.koppeling import KoppelingCreate

    for proto in Koppelprotocol:
        d = _basis()
        d["protocol"] = proto.value
        assert KoppelingCreate(**d).protocol == proto
    for impact in ImpactVerbreking:
        d = _basis()
        d["impact_bij_verbreking"] = impact.value
        assert KoppelingCreate(**d).impact_bij_verbreking == impact


def test_create_geen_serverbeheerde_velden():
    from schemas.koppeling import KoppelingCreate

    for veld in ("id", "tenant_id", "created_at", "updated_at"):
        assert veld not in KoppelingCreate.model_fields


def test_update_geen_ouder_fks():
    from schemas.koppeling import KoppelingUpdate

    assert "bron_applicatie_id" not in KoppelingUpdate.model_fields
    assert "doel_applicatie_id" not in KoppelingUpdate.model_fields


def test_update_partieel():
    from schemas.koppeling import KoppelingUpdate

    m = KoppelingUpdate(omschrijving="bijgewerkt")
    assert m.model_dump(exclude_unset=True) == {"omschrijving": "bijgewerkt"}


def test_update_null_op_verplicht_geweigerd():
    from schemas.koppeling import KoppelingUpdate

    with pytest.raises(ValidationError):
        KoppelingUpdate(richting=None)


def test_read_geen_tenant_id():
    from schemas.koppeling import KoppelingRead

    assert "tenant_id" not in KoppelingRead.model_fields
    assert "bron_applicatie_id" in KoppelingRead.model_fields
    assert "doel_applicatie_id" in KoppelingRead.model_fields
