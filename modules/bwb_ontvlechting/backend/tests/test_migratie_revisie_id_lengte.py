"""Handhaving: Alembic-revisie-id ≤ 32 tekens (LI049).

Alembic's `alembic_version.version_num` is standaard `VARCHAR(32)`. Een revisie-id
> 32 tekens laat `lk-migrate` falen op een verse provisioning
(`StringDataRightTruncation`) — een deploy-blocker die alleen bij een schone reseed
opduikt. Revisie `0043_adr030_contract_band_dekking` (33) schond dit ongemerkt omdat
de regel tot dusver alleen een skill-conventie was, niet machine-geborgd.

Deze test scant **beide** migratiebomen (platform `backend/alembic/versions` én
`modules/**/migrations/versions`) zodat het gat niet terugkeert.
"""
import pathlib
import re

# tests/ -> backend/ -> bwb_ontvlechting/ -> modules/ -> repo-root
ROOT = pathlib.Path(__file__).resolve().parents[4]

MIGRATIE_MAPPEN = [
    ROOT / "backend" / "alembic" / "versions",
    *(ROOT / "modules").glob("*/migrations/versions"),
]

MAX_LENGTE = 32  # Alembic alembic_version.version_num VARCHAR(32)
_REV_RE = re.compile(r"""^revision(?:\s*:\s*str)?\s*=\s*['"]([^'"]+)['"]""", re.M)


def _alle_revisie_ids():
    """Yield (revisie_id, bestand) over alle migratiebestanden in beide bomen."""
    for map_ in MIGRATIE_MAPPEN:
        if not map_.is_dir():
            continue
        for f in sorted(map_.glob("*.py")):
            if f.name == "__init__.py":
                continue
            m = _REV_RE.search(f.read_text(encoding="utf-8"))
            if m:
                yield m.group(1), f


def test_migratiemappen_gevonden():
    # Borgt dat de scan niet stilletjes 0 bestanden ziet (anders is de test nutteloos).
    ids = list(_alle_revisie_ids())
    assert len(ids) > 0, f"Geen revisie-ids gevonden in {MIGRATIE_MAPPEN}"


def test_alle_revisie_ids_max_32_tekens():
    overtreders = [
        (rid, len(rid), f.relative_to(ROOT).as_posix())
        for rid, f in _alle_revisie_ids()
        if len(rid) > MAX_LENGTE
    ]
    assert not overtreders, (
        "Revisie-id(s) > 32 tekens (breken alembic_version VARCHAR(32) bij verse "
        f"provisioning): {overtreders}"
    )


def test_predikaat_weigert_een_te_lang_id():
    # Tegenproef: het lengte-criterium faalt aantoonbaar op een 33-teken-id.
    te_lang = "0043_adr030_contract_band_dekking"  # 33 tekens (het oude id)
    assert len(te_lang) == 33
    assert len(te_lang) > MAX_LENGTE
    # en een conform id slaagt
    assert len("0043_adr030_contract_band") <= MAX_LENGTE
