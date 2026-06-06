"""Unit-tests — Datatype-schemas (P5-vervolg)."""
import uuid

import pytest
from pydantic import ValidationError


def _basis() -> dict:
    return {"applicatie_id": str(uuid.uuid4()), "categorie": "documenten"}


def test_create_happy_path():
    from schemas.datatype import DatatypeCreate

    m = DatatypeCreate(**_basis())
    assert m.categorie.value == "documenten"
    assert m.omschrijving is None


def test_create_extra_forbid():
    from schemas.datatype import DatatypeCreate

    with pytest.raises(ValidationError):
        DatatypeCreate(**_basis(), onbekend="x")


def test_create_ongeldige_categorie():
    from schemas.datatype import DatatypeCreate

    d = _basis()
    d["categorie"] = "geen-categorie"
    with pytest.raises(ValidationError):
        DatatypeCreate(**d)


def test_create_alle_categorieen():
    from models.models import DatatypeCategorie
    from schemas.datatype import DatatypeCreate

    for cat in DatatypeCategorie:
        d = _basis()
        d["categorie"] = cat.value
        assert DatatypeCreate(**d).categorie == cat


def test_create_ongeldige_applicatie_id():
    from schemas.datatype import DatatypeCreate

    d = _basis()
    d["applicatie_id"] = "geen-uuid"
    with pytest.raises(ValidationError):
        DatatypeCreate(**d)


def test_create_omvang_te_lang():
    from schemas.datatype import DatatypeCreate

    d = _basis()
    d["omvang_indicatie"] = "x" * 256
    with pytest.raises(ValidationError):
        DatatypeCreate(**d)


def test_create_geen_serverbeheerde_velden():
    from schemas.datatype import DatatypeCreate

    for veld in ("id", "tenant_id", "created_at", "updated_at"):
        assert veld not in DatatypeCreate.model_fields


def test_update_geen_applicatie_id():
    from schemas.datatype import DatatypeUpdate

    assert "applicatie_id" not in DatatypeUpdate.model_fields  # immutabel


def test_update_partieel():
    from schemas.datatype import DatatypeUpdate

    m = DatatypeUpdate(omschrijving="bijgewerkt")
    assert m.model_dump(exclude_unset=True) == {"omschrijving": "bijgewerkt"}


def test_update_extra_forbid():
    from schemas.datatype import DatatypeUpdate

    with pytest.raises(ValidationError):
        DatatypeUpdate(zzz=1)


def test_update_null_op_categorie_geweigerd():
    from schemas.datatype import DatatypeUpdate

    with pytest.raises(ValidationError):
        DatatypeUpdate(categorie=None)


def test_read_geen_tenant_id():
    from schemas.datatype import DatatypeRead

    assert "tenant_id" not in DatatypeRead.model_fields
    assert "applicatie_id" in DatatypeRead.model_fields
