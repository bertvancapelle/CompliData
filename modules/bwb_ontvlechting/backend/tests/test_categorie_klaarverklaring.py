"""Tests — categorie-klaarverklaring (ADR-027 slice 1).

Offline: schema-validatie (verplichte reden, status-allowlist), engine-import-afwezigheid, RBAC.
Live (skip-if-no-DB): maak_aan (happy/404/409/422), symmetrische statuswissel, RLS-isolatie,
audit-record bij aanmaken én bij statuswissel, en bewijs dat lifecycle/profiel ONgewijzigd blijft.
"""
import asyncio
import uuid

import pytest
from pydantic import ValidationError

import app.core.audit  # noqa: F401  (activeert de capture-hook)
import app.core.database  # noqa: F401
from app.core.tenant_context import (
    reset_audit_context,
    reset_tenant_context,
    zet_audit_context,
    zet_tenant_context,
)

_TID = "11111111-1111-1111-1111-111111111111"
_ANDER_TID = "22222222-2222-2222-2222-222222222222"
_CD_APP_URL = "postgresql+asyncpg://cd_app:changeme_dev@localhost:5432/complidata"


# ── Offline: schema-validatie ────────────────────────────────────────────────────
def test_create_reden_verplicht():
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate

    cid = uuid.uuid4()
    KlaarverklaringCreate(component_id=cid, categorie_nr=1, reden="beoordeeld, akkoord")
    for leeg in ("", "   "):
        with pytest.raises(ValidationError):
            KlaarverklaringCreate(component_id=cid, categorie_nr=1, reden=leeg)


def test_statuswijzig_validatie():
    from schemas.categorie_klaarverklaring import KlaarverklaringStatusWijzig

    KlaarverklaringStatusWijzig(status="open", reden="heropend wegens nieuwe info")
    with pytest.raises(ValidationError):  # ongeldige status
        KlaarverklaringStatusWijzig(status="afgehandeld", reden="x")
    with pytest.raises(ValidationError):  # lege reden
        KlaarverklaringStatusWijzig(status="klaar", reden="  ")


def test_create_geen_serverbeheerde_velden():
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate

    for veld in ("id", "tenant_id", "status", "verklaard_door", "verklaard_op", "created_at"):
        assert veld not in KlaarverklaringCreate.model_fields


# ── Offline: engine onaangeroerd ─────────────────────────────────────────────────
def test_klaarverklaring_service_raakt_engine_niet():
    import services.categorie_klaarverklaring_service as s

    for naam in (
        "lifecycle_service", "herbereken_lifecycle", "bepaal_lifecycle",
        "ComponentProfiel", "Blokkade", "Checklistscore",
    ):
        assert not hasattr(s, naam), f"klaarverklaring-service mag de engine niet importeren: {naam!r}"


# ── Offline: RBAC (inhoud-patroon) ───────────────────────────────────────────────
def test_klaarverklaring_rbac_inhoud_patroon():
    from app.core.rbac import Actie, Entiteit, heeft_permissie

    assert heeft_permissie(["viewer"], Entiteit.KLAARVERKLARING, Actie.LEZEN)
    assert heeft_permissie(["medewerker"], Entiteit.KLAARVERKLARING, Actie.AANMAKEN)
    assert heeft_permissie(["medewerker"], Entiteit.KLAARVERKLARING, Actie.WIJZIGEN)
    assert not heeft_permissie(["medewerker"], Entiteit.KLAARVERKLARING, Actie.VERWIJDEREN)
    assert heeft_permissie(["beheerder"], Entiteit.KLAARVERKLARING, Actie.VERWIJDEREN)
    assert not heeft_permissie(["viewer"], Entiteit.KLAARVERKLARING, Actie.AANMAKEN)


# ── Live (skip-if-no-DB) ─────────────────────────────────────────────────────────
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


integratie = pytest.mark.skipif(not _db_bereikbaar(), reason="cd_app-DB niet bereikbaar (offline)")


async def _run_rls(fn, tid=_TID):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    eng = create_async_engine(_CD_APP_URL)
    smf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
    tok = zet_tenant_context(tid)
    audit_tok = zet_audit_context(actor_sub="test:adr027", actor_email="adr027@test", correlatie_id=None)
    try:
        async with smf() as s:
            s.sync_session.info["rls"] = True
            return await fn(s)
    finally:
        reset_audit_context(audit_tok)
        reset_tenant_context(tok)
        await eng.dispose()


async def _maak_app_en_categorie(s, tid):
    """Maak een applicatie + lever een geldig categorie_nr voor componenttype 'applicatie'."""
    from sqlalchemy import select
    from models.models import ChecklistVraag
    from schemas.applicatie import ApplicatieCreate
    from services import applicatie_service

    app = await applicatie_service.maak_aan(
        s, tid, ApplicatieCreate(naam="WT-KV-App", hostingmodel="saas", migratiepad="onbekend",
                                 complexiteit="midden", prioriteit="midden"))
    cat = (await s.execute(
        select(ChecklistVraag.categorie_nr).where(ChecklistVraag.componenttype == "applicatie").limit(1)
    )).scalar_one()
    return app.id, cat


@integratie
def test_klaarverklaring_happy_statuswissel_audit_engine_live():
    """Happy aanmaak + symmetrische statuswissel + audit-historie + engine onaangeroerd."""
    from sqlalchemy import text as _text

    from services import categorie_klaarverklaring_service as svc
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate, KlaarverklaringStatusWijzig

    tid = uuid.UUID(_TID)

    async def _flow(s):
        ids = []
        try:
            app_id, cat = await _maak_app_en_categorie(s, tid)
            ids.append(app_id)
            lc_voor = (await s.execute(
                _text("SELECT lifecycle_status FROM component_profiel WHERE id=:i"), {"i": str(app_id)}
            )).scalar_one()

            obj = await svc.maak_aan(s, tid, KlaarverklaringCreate(
                component_id=app_id, categorie_nr=cat, reden="beoordeeld en akkoord"))
            assert obj.status.value == "klaar"
            assert obj.verklaard_door and obj.verklaard_op is not None

            n_na_create = (await s.execute(_text(
                "SELECT count(*) FROM audit_log WHERE entiteit_type='categorie_klaarverklaring' "
                "AND entiteit_id=:i"), {"i": str(obj.id)})).scalar_one()
            assert n_na_create >= 1

            o2 = await svc.wijzig_status(s, tid, obj.id, KlaarverklaringStatusWijzig(
                status="open", reden="heropend: scope gewijzigd"))
            assert o2.status.value == "open" and o2.reden == "heropend: scope gewijzigd"
            o3 = await svc.wijzig_status(s, tid, obj.id, KlaarverklaringStatusWijzig(
                status="klaar", reden="opnieuw afgehandeld"))
            assert o3.status.value == "klaar"

            n_na_wissel = (await s.execute(_text(
                "SELECT count(*) FROM audit_log WHERE entiteit_type='categorie_klaarverklaring' "
                "AND entiteit_id=:i"), {"i": str(obj.id)})).scalar_one()
            assert n_na_wissel > n_na_create
            laatste = (await s.execute(_text(
                "SELECT wijziging::text FROM audit_log WHERE entiteit_type='categorie_klaarverklaring' "
                "AND entiteit_id=:i ORDER BY tijdstip DESC LIMIT 1"), {"i": str(obj.id)})).scalar_one()
            assert "reden" in laatste and "status" in laatste

            lc_na = (await s.execute(
                _text("SELECT lifecycle_status FROM component_profiel WHERE id=:i"), {"i": str(app_id)}
            )).scalar_one()
            assert lc_na == lc_voor
        finally:
            for eid in ids:
                await s.execute(_text("DELETE FROM element WHERE id=:i"), {"i": str(eid)})
            await s.commit()

    asyncio.run(_run_rls(_flow))


@integratie
def test_klaarverklaring_404_onbekende_component_live():
    from services import categorie_klaarverklaring_service as svc
    from services.errors import NietGevonden
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate

    tid = uuid.UUID(_TID)

    async def _flow(s):
        with pytest.raises(NietGevonden):
            await svc.maak_aan(s, tid, KlaarverklaringCreate(
                component_id=uuid.uuid4(), categorie_nr=1, reden="x"))

    asyncio.run(_run_rls(_flow))


@integratie
def test_klaarverklaring_422_ongeldige_categorie_live():
    from sqlalchemy import text as _text

    from services import categorie_klaarverklaring_service as svc
    from services.errors import OngeldigeRegistratie
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate

    tid = uuid.UUID(_TID)

    async def _flow(s):
        ids = []
        try:
            app_id, _cat = await _maak_app_en_categorie(s, tid)
            ids.append(app_id)
            with pytest.raises(OngeldigeRegistratie) as exc:
                await svc.maak_aan(s, tid, KlaarverklaringCreate(
                    component_id=app_id, categorie_nr=99999, reden="x"))
            assert exc.value.code == "ONGELDIGE_CATEGORIE"
        finally:
            for eid in ids:
                await s.execute(_text("DELETE FROM element WHERE id=:i"), {"i": str(eid)})
            await s.commit()

    asyncio.run(_run_rls(_flow))


@integratie
def test_klaarverklaring_409_dubbel_live():
    from sqlalchemy import text as _text

    from services import categorie_klaarverklaring_service as svc
    from services.errors import RegistratieConflict
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate

    tid = uuid.UUID(_TID)

    async def _flow(s):
        ids = []
        try:
            app_id, cat = await _maak_app_en_categorie(s, tid)
            ids.append(app_id)
            await svc.maak_aan(s, tid, KlaarverklaringCreate(
                component_id=app_id, categorie_nr=cat, reden="afgehandeld"))
            with pytest.raises(RegistratieConflict) as exc:
                await svc.maak_aan(s, tid, KlaarverklaringCreate(
                    component_id=app_id, categorie_nr=cat, reden="nogmaals"))
            assert exc.value.code == "KLAARVERKLARING_BESTAAT_AL"
        finally:
            for eid in ids:
                await s.execute(_text("DELETE FROM element WHERE id=:i"), {"i": str(eid)})
            await s.commit()

    asyncio.run(_run_rls(_flow))


@integratie
def test_klaarverklaring_rls_isolatie_live():
    """Een andere tenant ziet de klaarverklaring niet (RLS + expliciet tenant-filter)."""
    from sqlalchemy import text as _text

    from services import categorie_klaarverklaring_service as svc
    from schemas.categorie_klaarverklaring import KlaarverklaringCreate

    tid = uuid.UUID(_TID)

    async def _maak(s):
        app_id, cat = await _maak_app_en_categorie(s, tid)
        obj = await svc.maak_aan(s, tid, KlaarverklaringCreate(
            component_id=app_id, categorie_nr=cat, reden="afgehandeld"))
        return app_id, obj.id

    app_id, kv_id = asyncio.run(_run_rls(_maak, tid=_TID))

    async def _ander(s):
        # Andere tenant: lijst moet leeg zijn voor dit component (RLS verbergt de rij).
        rijen = await svc.lijst(s, uuid.UUID(_ANDER_TID), component_id=app_id)
        return len(rijen)

    try:
        assert asyncio.run(_run_rls(_ander, tid=_ANDER_TID)) == 0
    finally:
        async def _op(s):
            await s.execute(_text("DELETE FROM element WHERE id=:i"), {"i": str(app_id)})
            await s.commit()
        asyncio.run(_run_rls(_op, tid=_TID))
