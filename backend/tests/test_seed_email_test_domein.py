"""Borging: 'wat je ziet = waarmee je inlogt' voor de dev-seed (gate, DC).

Twee invarianten, DB-loos (statische analyse van seed + realm-JSON):
  (a) elke login-capabele seeded gebruiker draagt in de app-content exact dezelfde
      e-mail als zijn Keycloak-login-mail in de realm;
  (b) elke e-mail in de dev-seed staat op het gereserveerde test-TLD '.test'
      (geen echt-ogende domeinen zoals .nl, geen .example meer).

Aanleiding: de realm seedde login-mails op '.test', terwijl dev_seed_testdata.py
content-mails op '.nl' had -> inloggen met het getoonde adres faalde.

De login-koppelingen (Keycloak-sub <-> persoonsnaam) worden uit de seed zelf
afgeleid (ADR-029 `_seed_dev_gebruikers`), zodat de test niet los kan lopen van
de werkelijke koppeling.
"""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
SEED = REPO / "backend" / "dev_seed_testdata.py"
REALM = REPO / "keycloak" / "realms" / "likara-realm.json"

# E-mail-TLD: het stuk na de laatste punt van het domein.
_EMAIL_TLD_RE = re.compile(r"@[A-Za-z0-9.-]+\.([A-Za-z]{2,})\b")
# Koppeling uit _seed_dev_gebruikers: ("<keycloak-sub>", "<persoonsnaam>").
_KOPPELING_RE = re.compile(r'\("(aaaaaaaa-[0-9a-f-]+)",\s*"([^"]+)"\)')


def _niet_test_tlds(src: str) -> set[str]:
    """TLD's van e-mails in `src` die niet '.test' zijn."""
    return {tld.lower() for tld in _EMAIL_TLD_RE.findall(src)} - {"test"}


def _login_mismatches(seed_src: str, realm: dict) -> list[str]:
    """Login-capabele koppelingen waarvan de content-mail (seed) afwijkt van de
    realm-login-mail. Lege lijst = consistent."""
    realm_mail_by_id = {
        u["id"]: u["email"]
        for u in realm.get("users", [])
        if "id" in u and "email" in u
    }
    problemen = []
    for sub, naam in _KOPPELING_RE.findall(seed_src):
        realm_mail = realm_mail_by_id.get(sub)
        if not realm_mail:
            problemen.append(f"{naam}: realm mist user-id {sub}")
            continue
        # Content-mail van deze persoon: naam + e-mail op dezelfde seed-regel.
        regel = re.search(
            r'"' + re.escape(naam) + r'"[^\n]*?"([^"@\n]+@[^"\n]+)"', seed_src
        )
        if not regel:
            problemen.append(f"{naam}: geen content-mail in de seed gevonden")
            continue
        if regel.group(1) != realm_mail:
            problemen.append(
                f"{naam}: content {regel.group(1)} != realm {realm_mail}"
            )
    return problemen


# ── Live borging tegen de echte bestanden ────────────────────────────────────

def test_alle_seed_mails_op_test_domein():
    afwijkend = _niet_test_tlds(SEED.read_text(encoding="utf-8"))
    assert not afwijkend, f"seed-mails met niet-.test TLD: {sorted(afwijkend)}"


def test_login_content_mail_gelijk_aan_realm():
    seed_src = SEED.read_text(encoding="utf-8")
    realm = json.loads(REALM.read_text(encoding="utf-8"))
    mismatches = _login_mismatches(seed_src, realm)
    assert not mismatches, "login-mail != content-mail:\n  " + "\n  ".join(mismatches)

    # Borg dat er daadwerkelijk koppelingen zijn (anders is de test loos groen).
    assert _KOPPELING_RE.findall(seed_src), "geen dev-gebruiker-koppelingen gevonden"


# ── Bijt-bewijs (groen -> rood -> groen) met fixtures, raakt geen echt bestand ─

def test_borging_bijt_op_niet_test_domein():
    """ROOD-bewijs (b): één heringevoerd .nl-adres wordt gedetecteerd."""
    goed = '("J. de Vries", "06", "j.devries@bvowb.test"),\n'
    fout = '("J. de Vries", "06", "j.devries@bvowb.nl"),\n'
    assert _niet_test_tlds(goed) == set()
    assert _niet_test_tlds(fout) == {"nl"}


def test_borging_bijt_op_login_mismatch():
    """ROOD-bewijs (a): content-mail die afwijkt van de realm-login-mail valt op."""
    realm = {
        "users": [
            {"id": "aaaaaaaa-0001-0001-0001-000000000001",
             "email": "j.devries@bvowb.test"}
        ]
    }
    sub_regel = '        ("aaaaaaaa-0001-0001-0001-000000000001", "J. de Vries"),\n'

    consistent = sub_regel + '("J. de Vries", "x", "j.devries@bvowb.test"),\n'
    assert _login_mismatches(consistent, realm) == []

    mismatch = sub_regel + '("J. de Vries", "x", "j.devries@elders.test"),\n'
    problemen = _login_mismatches(mismatch, realm)
    assert problemen and "J. de Vries" in problemen[0]
