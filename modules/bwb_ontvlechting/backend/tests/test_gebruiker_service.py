"""Tests — gebruikersbeheer (ADR-029 Fase 2).

Offline: schema-validatie, engine-import-afwezigheid, RBAC (GEBRUIKERSBEHEER), wachtwoord-
generator, en de service-foutpaden (email-duplicaat / Keycloak-fout-rollback / commit-fout-
cleanup) met gemockte sessie + gemockte Keycloak. Live (skip-if-no-DB): happy aanmaak + naam-join
+ engine-geen-mutatie. Keycloak wordt overal gemockt — geen live IAM in de tests.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

import app.core.audit  # noqa: F401  (capture-hook)
import app.core.database  # noqa: F401
from app.core.tenant_context import (
    reset_audit_context,
    reset_tenant_context,
    zet_audit_context,
    zet_tenant_context,
)

_TID = "11111111-1111-1111-1111-111111111111"
_CD_APP_URL = "postgresql+asyncpg://lk_app:changeme_dev@localhost:5432/likara"


def _result(val):
    r = MagicMock()
    r.scalar_one_or_none.return_value = val
    return r


# ── Offline: schema's ─────────────────────────────────────────────────────────
def test_request_geen_wachtwoordveld_en_extra_forbid():
    from schemas.gebruiker import GebruikerAanmakenRequest

    ok = GebruikerAanmakenRequest(naam="Jan Jansen", email="Jan@Org.NL")
    assert ok.email == "jan@org.nl" and ok.rol == "medewerker"  # genormaliseerd + default
    with pytest.raises(ValidationError):  # wachtwoord meesturen mag niet (extra=forbid)
        GebruikerAanmakenRequest(naam="Jan", email="jan@org.nl", tijdelijk_wachtwoord="x")
    with pytest.raises(ValidationError):  # ongeldig e-mailadres
        GebruikerAanmakenRequest(naam="Jan", email="geen-email")
    with pytest.raises(ValidationError):  # rol buiten de allowlist
        GebruikerAanmakenRequest(naam="Jan", email="jan@org.nl", rol="beheerder")


def test_read_schema_bevat_geen_wachtwoord():
    from schemas.gebruiker import GebruikerPersoonRead

    assert "tijdelijk_wachtwoord" not in GebruikerPersoonRead.model_fields
    assert "wachtwoord" not in GebruikerPersoonRead.model_fields


# ── Offline: engine-borging (import-afwezigheid) ───────────────────────────────
def test_gebruiker_service_raakt_engine_niet():
    import services.gebruiker_service as s

    for naam in ("lifecycle_service", "herbereken_lifecycle", "bepaal_lifecycle",
                 "ComponentProfiel", "Blokkade", "Checklistscore"):
        assert not hasattr(s, naam), f"gebruiker-service mag de engine niet importeren: {naam!r}"


# ── Offline: RBAC ──────────────────────────────────────────────────────────────
def test_gebruikersbeheer_alleen_beheerder():
    from app.core.rbac import Actie, Entiteit, heeft_permissie

    assert heeft_permissie(["beheerder"], Entiteit.GEBRUIKERSBEHEER, Actie.AANMAKEN)
    assert heeft_permissie(["beheerder"], Entiteit.GEBRUIKERSBEHEER, Actie.LEZEN)
    for rol in ("viewer", "medewerker", "auditor"):
        assert not heeft_permissie([rol], Entiteit.GEBRUIKERSBEHEER, Actie.LEZEN)
        assert not heeft_permissie([rol], Entiteit.GEBRUIKERSBEHEER, Actie.AANMAKEN)


# ── Offline: wachtwoord-generator ──────────────────────────────────────────────
def test_wachtwoord_generator_sterk_en_uniek():
    from app.core.keycloak import genereer_tijdelijk_wachtwoord

    pws = {genereer_tijdelijk_wachtwoord() for _ in range(20)}
    assert len(pws) == 20  # willekeurig (geen botsingen)
    for pw in pws:
        assert len(pw) >= 16
        assert any(c.isupper() for c in pw) and any(c.isdigit() for c in pw)


# ── Offline: service-foutpaden (gemockte sessie + Keycloak) ─────────────────────
def _patch_kc(monkeypatch, *, sub="kc-sub-1", fout=False):
    import services.gebruiker_service as svc

    async def _maak(**_k):
        if fout:
            from app.core.keycloak import KeycloakProvisioningFout
            raise KeycloakProvisioningFout("KC down", 502)
        return sub

    monkeypatch.setattr(svc.keycloak, "maak_keycloak_gebruiker", _maak)
    monkeypatch.setattr(svc.keycloak, "deactiveer_keycloak_gebruiker", AsyncMock())
    return svc


def test_maak_gebruiker_email_al_in_gebruik(monkeypatch):
    svc = _patch_kc(monkeypatch)
    from services.errors import OngeldigeRegistratie

    session = AsyncMock()
    session.execute = AsyncMock(return_value=_result(uuid.uuid4()))  # email al gekoppeld
    with pytest.raises(OngeldigeRegistratie) as exc:
        asyncio.run(svc.maak_gebruiker(
            session, _TID, naam="Jan", email="jan@org.nl", afdeling_id=uuid.uuid4(),
            functietitel=None, rol="medewerker"))
    assert exc.value.code == "EMAIL_AL_IN_GEBRUIK"


def test_maak_gebruiker_kc_fout_rollt_terug(monkeypatch):
    svc = _patch_kc(monkeypatch, fout=True)
    from services.errors import KeycloakNietBeschikbaar

    async def _persoon(*a, **k):
        return SimpleNamespace(id=uuid.uuid4(), naam="Jan", email="jan@org.nl")

    monkeypatch.setattr(svc.partij_service, "maak_persoon_flush", _persoon)
    session = AsyncMock()
    session.execute = AsyncMock(return_value=_result(None))  # email vrij
    with pytest.raises(KeycloakNietBeschikbaar):
        asyncio.run(svc.maak_gebruiker(
            session, _TID, naam="Jan", email="jan@org.nl", afdeling_id=uuid.uuid4(),
            functietitel=None, rol="medewerker"))
    session.rollback.assert_awaited()           # DB teruggerold (geen half-aangemaakte persoon)
    session.commit.assert_not_awaited()


def test_maak_gebruiker_commit_fout_deactiveert_kc(monkeypatch):
    svc = _patch_kc(monkeypatch, sub="kc-sub-9")
    from services.errors import KeycloakNietBeschikbaar

    async def _persoon(*a, **k):
        return SimpleNamespace(id=uuid.uuid4(), naam="Jan", email="jan@org.nl")

    monkeypatch.setattr(svc.partij_service, "maak_persoon_flush", _persoon)
    session = AsyncMock()
    session.execute = AsyncMock(return_value=_result(None))
    session.add = MagicMock()
    session.commit = AsyncMock(side_effect=RuntimeError("commit faalt"))
    with pytest.raises(KeycloakNietBeschikbaar):
        asyncio.run(svc.maak_gebruiker(
            session, _TID, naam="Jan", email="jan@org.nl", afdeling_id=uuid.uuid4(),
            functietitel=None, rol="medewerker"))
    # Orphan-cleanup: het al-aangemaakte KC-account wordt gedeactiveerd.
    svc.keycloak.deactiveer_keycloak_gebruiker.assert_awaited_once_with("kc-sub-9")


# ── Live (skip-if-no-DB) ───────────────────────────────────────────────────────
def _db_bereikbaar() -> bool:
    async def _probe():
        from sqlalchemy.ext.asyncio import create_async_engine

        eng = create_async_engine(_CD_APP_URL)
        try:
            async with eng.connect():
                return True
        except Exception:
            return False
        finally:
            await eng.dispose()

    try:
        return asyncio.run(_probe())
    except Exception:
        return False


integratie = pytest.mark.skipif(not _db_bereikbaar(), reason="lk_app-DB niet bereikbaar (offline)")


async def _run_rls(fn, tid=_TID):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    eng = create_async_engine(_CD_APP_URL)
    smf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
    tok = zet_tenant_context(tid)
    audit_tok = zet_audit_context(actor_sub="test:adr029", actor_email="adr029@test", correlatie_id=None)
    try:
        async with smf() as s:
            s.sync_session.info["rls"] = True
            return await fn(s)
    finally:
        reset_audit_context(audit_tok)
        reset_tenant_context(tok)
        await eng.dispose()


@integratie
def test_maak_gebruiker_live_happy_en_geen_mutatie(monkeypatch):
    """Volledige flow tegen de DB met gemockte Keycloak: persoon + koppelrij ontstaan, naam-join
    klopt, en de lifecycle van een los component blijft ongewijzigd (engine onaangeroerd)."""
    from sqlalchemy import text as _text

    from schemas.applicatie import ApplicatieCreate
    from schemas.partij import PartijCreate
    from services import applicatie_service, gebruiker_service, partij_service
    from models.models import PartijAard

    # KC-provisioning mocken (geen live IAM): vaste sub.
    async def _kc(**_k):
        return f"kc-{uuid.uuid4()}"

    monkeypatch.setattr(gebruiker_service.keycloak, "maak_keycloak_gebruiker", _kc)

    tid = uuid.UUID(_TID)
    email = f"wt-{uuid.uuid4().hex[:8]}@org.test"

    async def _flow(s):
        ids = []
        try:
            org = await partij_service.maak_aan(s, tid, PartijCreate(aard=PartijAard.organisatie, naam="WT-Org"))
            afd = await partij_service.maak_aan(s, tid, PartijCreate(
                aard=PartijAard.organisatie_eenheid, naam="WT-Afd", organisatie_id=org.id))
            app = await applicatie_service.maak_aan(s, tid, ApplicatieCreate(
                naam="WT-GebrApp", hostingmodel="saas", migratiepad="onbekend",
                complexiteit="midden", prioriteit="midden"))
            ids += [org.id, afd.id, app.id]
            lc_voor = (await s.execute(
                _text("SELECT lifecycle_status FROM component_profiel WHERE id=:i"), {"i": str(app.id)}
            )).scalar_one()

            read, wachtwoord = await gebruiker_service.maak_gebruiker(
                s, tid, naam="Wendy Test", email=email, afdeling_id=afd.id,
                functietitel="Analist", rol="medewerker")
            ids.append(read.persoon_id)

            assert read.naam == "Wendy Test" and read.email == email
            assert wachtwoord and len(wachtwoord) >= 16
            n = (await s.execute(_text(
                "SELECT count(*) FROM gebruiker_persoon WHERE persoon_id=:p"), {"p": str(read.persoon_id)}
            )).scalar_one()
            assert n == 1

            lc_na = (await s.execute(
                _text("SELECT lifecycle_status FROM component_profiel WHERE id=:i"), {"i": str(app.id)}
            )).scalar_one()
            assert lc_na == lc_voor  # engine onaangeroerd

            # lijst toont de gebruiker met naam
            items, _ = await gebruiker_service.lijst_gebruikers(s, tid, limit=100)
            assert any(i.persoon_id == read.persoon_id and i.naam == "Wendy Test" for i in items)
        finally:
            # Leaf-first: persoon (→ cascade koppelrij) + app, dán afdeling, dán org —
            # `fk_partij_organisatie`/lidmaatschap is ON DELETE RESTRICT (reversed = persoon,app,afd,org).
            for eid in reversed(ids):
                await s.execute(_text("DELETE FROM element WHERE id=:i"), {"i": str(eid)})
            await s.commit()

    asyncio.run(_run_rls(_flow))
