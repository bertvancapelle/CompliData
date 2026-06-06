"""Unit-tests — Gebruikersgroep-schemas (P5-vervolg)."""
import uuid

import pytest
from pydantic import ValidationError


def _basis() -> dict:
    return {"applicatie_id": str(uuid.uuid4()), "organisatie": "Gemeente Veldendam"}


def test_create_happy_path():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    m = GebruikersgroepCreate(**_basis(), afdeling="Burgerzaken", aantal_gebruikers=12)
    assert m.organisatie == "Gemeente Veldendam"
    assert m.aantal_gebruikers == 12


def test_create_extra_forbid():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    with pytest.raises(ValidationError):
        GebruikersgroepCreate(**_basis(), onbekend="x")


def test_create_organisatie_vrije_tekst():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    d = _basis()
    d["organisatie"] = "Willekeurige Dienst BV"
    assert GebruikersgroepCreate(**d).organisatie == "Willekeurige Dienst BV"


def test_create_organisatie_leeg_geweigerd():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    d = _basis()
    d["organisatie"] = "   "
    with pytest.raises(ValidationError):
        GebruikersgroepCreate(**d)


def test_create_organisatie_te_lang():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    d = _basis()
    d["organisatie"] = "x" * 121
    with pytest.raises(ValidationError):
        GebruikersgroepCreate(**d)


def test_create_aantal_negatief_geweigerd():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    with pytest.raises(ValidationError):
        GebruikersgroepCreate(**_basis(), aantal_gebruikers=-1)


def test_create_aantal_nul_toegestaan():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    assert GebruikersgroepCreate(**_basis(), aantal_gebruikers=0).aantal_gebruikers == 0


def test_create_geen_serverbeheerde_velden():
    from schemas.gebruikersgroep import GebruikersgroepCreate

    for veld in ("id", "tenant_id", "created_at", "updated_at"):
        assert veld not in GebruikersgroepCreate.model_fields


def test_update_geen_applicatie_id():
    from schemas.gebruikersgroep import GebruikersgroepUpdate

    assert "applicatie_id" not in GebruikersgroepUpdate.model_fields  # immutabel


def test_update_null_op_organisatie_geweigerd():
    from schemas.gebruikersgroep import GebruikersgroepUpdate

    with pytest.raises(ValidationError):
        GebruikersgroepUpdate(organisatie=None)


def test_update_aantal_negatief_geweigerd():
    from schemas.gebruikersgroep import GebruikersgroepUpdate

    with pytest.raises(ValidationError):
        GebruikersgroepUpdate(aantal_gebruikers=-5)


def test_update_afdeling_wissen_toegestaan():
    from schemas.gebruikersgroep import GebruikersgroepUpdate

    m = GebruikersgroepUpdate(afdeling=None)
    assert "afdeling" in m.model_fields_set and m.afdeling is None


def test_read_geen_tenant_id():
    from schemas.gebruikersgroep import GebruikersgroepRead

    assert "tenant_id" not in GebruikersgroepRead.model_fields
    assert "applicatie_id" in GebruikersgroepRead.model_fields
