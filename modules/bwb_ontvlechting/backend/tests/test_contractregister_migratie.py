"""Structurele migratie-asserts — ADR-020 `0005_contractregister` (CD040).

Offline (geen live DB), conform de offline-grens: leest de migratiebron en borgt
de revisieketen, de RLS-boilerplate per tenant-tabel, de least-privilege-grants en
de enum-/CHECK-definitie. Het live RLS-/grants-/round-trip-gedrag wordt aanvullend
bij validatie gerenderd (`alembic upgrade 0004_bio2_bbn:0005_contractregister --sql`)
en eenmalig empirisch tegen de draaiende stack geverifieerd.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
MIGRATIE = (
    ROOT / "modules" / "bwb_ontvlechting" / "migrations" / "versions"
    / "0005_contractregister.py"
)


def _bron() -> str:
    return MIGRATIE.read_text(encoding="utf-8")


def test_migratie_bestaat_en_ketent_aan_head():
    bron = _bron()
    assert 'revision: str = "0005_contractregister"' in bron
    assert 'down_revision: Union[str, Sequence[str], None] = "0004_bio2_bbn"' in bron


def test_rls_boilerplate_per_tenant_tabel():
    bron = _bron()
    for tabel in ["leverancier", "contract", "contract_dekking",
                  "contract_kostenmodel", "applicatie_contract"]:
        assert tabel in bron, f"tenant-tabel ontbreekt in migratie: {tabel}"
    assert "ENABLE ROW LEVEL SECURITY" in bron
    assert "FORCE ROW LEVEL SECURITY" in bron
    assert "CREATE POLICY tenant_isolation" in bron
    assert "current_setting('app.tenant_id')::uuid" in bron
    assert "GRANT SELECT, INSERT, UPDATE, DELETE ON {tabel} TO cd_app" in bron


def test_catalogus_grants_least_privilege():
    bron = _bron()
    assert "REVOKE ALL ON contractconfig_optie FROM cd_app" in bron
    assert "GRANT SELECT ON contractconfig_optie TO cd_app" in bron
    assert "GRANT SELECT, INSERT, UPDATE ON contractconfig_optie TO cd_platform" in bron
    assert "GRANT USAGE, SELECT ON SEQUENCE contractconfig_optie_id_seq TO cd_platform" in bron
    # géén DELETE-grant op de catalogus (soft-deactivate = UPDATE, Addendum B).
    assert "DELETE ON contractconfig_optie" not in bron


def test_enums_en_check_aanwezig():
    bron = _bron()
    assert 'name="contracttype_enum"' in bron
    assert 'name="contractconfig_dimensie_enum"' in bron
    assert "ck_contract_mantel_consistentie" in bron
