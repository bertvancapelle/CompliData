"""Tests — dev-seed Aanvulling D contractlandschap (CD046).

Data-shape + dekkingsdoelen + naamgeving (offline, geen DB). De runtime-idempotentie
(tweemaal draaien → identieke tellingen) wordt live geverifieerd in de seed-run (poort 5);
de seed-functie is daarvoor opgebouwd met bestaans-checks op naam/sleutel/(app,contract).
"""
from collections import Counter

import dev_seed_testdata as seed

_DEKKING = {"licentie_aanschaf", "onderhoud_support", "hosting"}
_KOSTENMODEL = {"saas_pxq", "volume", "per_inwoner"}
_ROLLEN = {"valt_onder", "onderhoud", "hosting"}


def _alle_namen():
    namen = [l["naam"] for l in seed.LEVERANCIERS_D]
    namen += [c["contractnaam"] for c in seed.CONTRACTEN_D]
    namen += [naam for _, naam, _ in seed.KOPPELINGEN_D]
    return namen


def test_aantallen_4_leveranciers_7_contracten():
    assert len(seed.LEVERANCIERS_D) == 4
    assert len(seed.CONTRACTEN_D) == 7


def test_geen_tiel_in_namen():
    for naam in _alle_namen():
        assert "tiel" not in naam.lower(), naam


def test_alle_9_catalogus_opties_gebruikt():
    dekking, kostenmodel = set(), set()
    for c in seed.CONTRACTEN_D:
        dekking.update(c.get("dekking", []))
        kostenmodel.update(c.get("kostenmodel", []))
    rollen = {rol for _, _, rol in seed.KOPPELINGEN_D}
    assert dekking == _DEKKING
    assert kostenmodel == _KOSTENMODEL
    assert rollen == _ROLLEN


def test_drie_contracttypen_en_mantel_hierarchie_met_leverancier_erving():
    typen = {c["type"] for c in seed.CONTRACTEN_D}
    assert typen == {"mantelcontract", "deelcontract", "los_contract"}
    per_naam = {c["contractnaam"]: c for c in seed.CONTRACTEN_D}
    deel = [c for c in seed.CONTRACTEN_D if c["type"] == "deelcontract"]
    assert deel, "verwacht ten minste één deelcontract"
    for c in deel:
        mantel = per_naam[c["mantel"]]
        assert mantel["type"] == "mantelcontract"          # I1-spiegeling
        assert mantel["leverancier"] == c["leverancier"]   # I2: leverancier-erving


def test_multi_contract_app_en_apps_zonder_contract():
    per_app = Counter(idx for idx, _, _ in seed.KOPPELINGEN_D)
    assert max(per_app.values()) >= 3  # ≥1 multi-contract-app

    gekoppeld = set(per_app)
    alle = set(range(1, len(seed.APPS) + 1))
    zonder = alle - gekoppeld
    assert len(zonder) >= 2  # ≥2 apps bewust zonder contractkoppeling


def test_koppelingen_verwijzen_naar_bestaande_contracten_en_apps():
    contractnamen = {c["contractnaam"] for c in seed.CONTRACTEN_D}
    for app_idx, contractnaam, rol in seed.KOPPELINGEN_D:
        assert 1 <= app_idx <= len(seed.APPS)
        assert contractnaam in contractnamen
        assert rol in _ROLLEN
