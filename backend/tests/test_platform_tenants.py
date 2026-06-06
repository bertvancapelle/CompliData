"""Tests — tenant-onboarding input-validatie (ADR-012), offline."""
import pytest
from pydantic import ValidationError

from app.schemas.platform import TenantAanmaken


def test_tenant_aanmaken_geldig():
    t = TenantAanmaken(naam="Gemeente Tiel", slug="tiel")
    assert t.naam == "Gemeente Tiel"
    assert t.slug == "tiel"


def test_tenant_slug_genormaliseerd_en_gevalideerd():
    assert TenantAanmaken(naam="X", slug="West-Betuwe").slug == "west-betuwe"
    with pytest.raises(ValidationError):
        TenantAanmaken(naam="X", slug="ongeldige slug!")  # spatie/teken
    with pytest.raises(ValidationError):
        TenantAanmaken(naam="X", slug="a")  # te kort


def test_tenant_extra_veld_geweigerd():
    with pytest.raises(ValidationError):
        TenantAanmaken(naam="X", slug="x1", rol="beheerder")  # extra=forbid


def test_tenant_lege_naam_geweigerd():
    with pytest.raises(ValidationError):
        TenantAanmaken(naam="   ", slug="x1")
