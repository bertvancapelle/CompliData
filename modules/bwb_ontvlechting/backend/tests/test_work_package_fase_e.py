"""Tests — ADR-023 Fase E (E2): Work Package + hiërarchie.

Offline: model (element-subtype + composiet self-FK RESTRICT + CHECK), schema, RBAC,
audit-allowlist + de regressie-borging dat de work_package-laag de engine NIET raakt.
Live (skip-if-no-DB): CRUD, hiërarchie + subboom, cycluspreventie (self-parent +
transitieve kring + geldige diepe keten), verwijdergedrag (RESTRICT/409 + kind niet
geweesd), RLS-isolatie, audit-capture. Live-tests ruimen hun element-rijen structureel op.
"""
import asyncio
import uuid

import pytest

import app.core.audit  # noqa: F401 — registreert de audit-capture-hook
import app.core.database  # noqa: F401 — registreert de tenant-context-hook
from app.core.tenant_context import (
    reset_audit_context,
    reset_tenant_context,
    zet_audit_context,
    zet_tenant_context,
)

_TID = "11111111-1111-1111-1111-111111111111"
_TID_B = "22222222-2222-2222-2222-222222222222"
_LK_APP_URL = "postgresql+asyncpg://lk_app:changeme_dev@localhost:5432/likara"


# ── Offline: model + schema ──────────────────────────────────────────────────────

def test_work_package_is_element_subtype_met_self_fk():
    from models.models import WorkPackage

    assert WorkPackage.__tablename__ == "work_package"
    fks = {
        con.name: con
        for con in WorkPackage.__table__.constraints
        if con.__class__.__name__ == "ForeignKeyConstraint"
    }
    # shared-PK → element(tenant_id,id), cascade.
    assert "fk_work_package_element" in fks
    assert fks["fk_work_package_element"].ondelete == "CASCADE"
    # composiet self-FK met RESTRICT (subboom niet stilzwijgend wegvagen).
    assert "fk_work_package_bovenliggend" in fks
    assert fks["fk_work_package_bovenliggend"].ondelete == "RESTRICT"
    kols = WorkPackage.__table__.columns
    assert "naam" in kols and "toelichting" in kols and "bovenliggend_id" in kols


def test_work_package_check_geen_self_parent():
    from models.models import WorkPackage

    checks = [
        con.name for con in WorkPackage.__table__.constraints
        if con.__class__.__name__ == "CheckConstraint"
    ]
    assert "ck_work_package_geen_self_parent" in checks


def test_work_package_schema_validatie():
    from pydantic import ValidationError
    from schemas.work_package import WorkPackageCreate

    ok = WorkPackageCreate(naam="Migratie financieel domein")
    assert ok.bovenliggend_id is None
    WorkPackageCreate(naam="Sub", bovenliggend_id=uuid.uuid4())
    with pytest.raises(ValidationError):  # naam verplicht
        WorkPackageCreate(naam="  ")
    with pytest.raises(ValidationError):  # extra veld verboden
        WorkPackageCreate(naam="X", onbekend="y")


# ── Offline: RBAC + audit + regressie ────────────────────────────────────────────

def test_work_package_in_audit_allowlist():
    from app.core.audit import AUDIT_TENANT_ENTITEITEN

    assert "work_package" in AUDIT_TENANT_ENTITEITEN


def test_work_package_in_rbac_inhoud_patroon():
    from app.core.rbac import Actie, Entiteit, heeft_permissie

    assert heeft_permissie(["medewerker"], Entiteit.WORK_PACKAGE, Actie.AANMAKEN)
    assert heeft_permissie(["beheerder"], Entiteit.WORK_PACKAGE, Actie.VERWIJDEREN)
    assert not heeft_permissie(["viewer"], Entiteit.WORK_PACKAGE, Actie.AANMAKEN)
    assert heeft_permissie(["auditor"], Entiteit.WORK_PACKAGE, Actie.LEZEN)


def test_work_package_service_raakt_engine_niet():
    """Score blijft de enige lifecycle-driver: de work_package-service importeert géén
    engine-onderdeel (geen tweede driver via de migratielaag)."""
    import services.work_package_service as wps

    for naam in (
        "lifecycle_service", "herbereken_lifecycle", "bepaal_lifecycle",
        "ComponentProfiel", "Blokkade", "Checklistscore",
    ):
        assert not hasattr(wps, naam), f"work_package_service mag de engine niet importeren: {naam!r}"


# ── Live (skip-if-no-DB) ─────────────────────────────────────────────────────────

def _db_bereikbaar() -> bool:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    async def _check():
        eng = create_async_engine(_LK_APP_URL)
        try:
            async with eng.connect() as c:
                await c.execute(text("SELECT 1"))
            return True
        finally:
            await eng.dispose()
    try:
        return asyncio.run(_check())
    except Exception:
        return False


integratie = pytest.mark.skipif(not _db_bereikbaar(), reason="lk_app-DB niet bereikbaar (offline)")


async def _run_rls(tenant, actor, fn):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    eng = create_async_engine(_LK_APP_URL)
    smf = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
    ttok = zet_tenant_context(tenant)
    atok = zet_audit_context(actor, f"{actor}@test")
    try:
        async with smf() as s:
            s.sync_session.info["rls"] = True
            return await fn(s)
    finally:
        reset_audit_context(atok)
        reset_tenant_context(ttok)
        await eng.dispose()


async def _ruim(s, ids):
    """Verwijder de work_package-element-rijen leaf→root (RESTRICT-veilig)."""
    from sqlalchemy import text as _text

    for eid in reversed(ids):  # ids in aanmaakvolgorde root→leaf → omgekeerd opruimen
        await s.execute(_text("DELETE FROM element WHERE id=:i"), {"i": str(eid)})
    await s.commit()


@integratie
def test_work_package_crud_hierarchie_en_subboom_live():
    from schemas.work_package import WorkPackageCreate
    from services import work_package_service as svc

    async def _flow(s):
        ids = []
        try:
            a = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Test Financieel domein"))
            ids.append(a["id"])
            b = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Test Oracle-DB overzetten", bovenliggend_id=a["id"]))
            ids.append(b["id"])
            c = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Test Rapportages herbouwen", bovenliggend_id=b["id"]))
            ids.append(c["id"])
            subboom = await svc.subboom(s, _TID, a["id"])
            return a, b, c, subboom
        finally:
            await _ruim(s, ids)

    a, b, c, subboom = asyncio.run(_run_rls(_TID, "test:bert", _flow))
    assert b["bovenliggend_id"] == a["id"] and c["bovenliggend_id"] == b["id"]
    per_id = {x["id"]: x for x in subboom}
    assert per_id[b["id"]]["niveau"] == 1 and per_id[c["id"]]["niveau"] == 2
    assert per_id[c["id"]]["pad"][-1] == "WP-Test Rapportages herbouwen"


@integratie
def test_work_package_cycluspreventie_live():
    from schemas.work_package import WorkPackageCreate, WorkPackageUpdate
    from services import work_package_service as svc
    from services.errors import OngeldigeRegistratie

    async def _flow(s):
        ids = []
        try:
            a = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Cyc A"))
            ids.append(a["id"])
            b = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Cyc B", bovenliggend_id=a["id"]))
            ids.append(b["id"])
            c = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Cyc C", bovenliggend_id=b["id"]))
            ids.append(c["id"])
            fouten = {}
            # Self-parent.
            try:
                await svc.werk_bij(s, _TID, a["id"], WorkPackageUpdate(bovenliggend_id=a["id"]))
            except OngeldigeRegistratie as e:
                fouten["self"] = e.code
            # Transitieve kring: A onder C (C is afstammeling van A).
            try:
                await svc.werk_bij(s, _TID, a["id"], WorkPackageUpdate(bovenliggend_id=c["id"]))
            except OngeldigeRegistratie as e:
                fouten["kring"] = e.code
            # Geldige herhang: C los van B naar direct onder A (geen kring).
            herhang = await svc.werk_bij(s, _TID, c["id"], WorkPackageUpdate(bovenliggend_id=a["id"]))
            return fouten, herhang
        finally:
            await _ruim(s, ids)

    fouten, herhang = asyncio.run(_run_rls(_TID, "test:bert", _flow))
    assert fouten == {"self": "CYCLISCHE_HIERARCHIE", "kring": "CYCLISCHE_HIERARCHIE"}
    assert herhang["bovenliggend_id"] is not None  # geldige herhang slaagde


@integratie
def test_work_package_verwijdergedrag_live():
    from sqlalchemy import text as _text
    from schemas.work_package import WorkPackageCreate
    from services import work_package_service as svc
    from services.errors import RegistratieConflict

    async def _flow(s):
        ids = []
        try:
            p = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Del Ouder"))
            ids.append(p["id"])
            kind = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Del Kind", bovenliggend_id=p["id"]))
            ids.append(kind["id"])
            # Ouder met kind → 409, geen wegvagen.
            geweigerd = None
            try:
                await svc.verwijder(s, _TID, p["id"])
            except RegistratieConflict as e:
                geweigerd = e.code
            # Kind bestaat nog én is niet geweesd (bovenliggend_id intact).
            na = (await s.execute(_text(
                "SELECT bovenliggend_id FROM work_package WHERE id=:i"), {"i": str(kind["id"])})).scalar()
            # Kind eerst weg, dan ouder → mag.
            await svc.verwijder(s, _TID, kind["id"])
            ids.remove(kind["id"])
            await svc.verwijder(s, _TID, p["id"])
            ids.remove(p["id"])
            return geweigerd, na, p["id"]
        finally:
            await _ruim(s, ids)

    geweigerd, kind_parent, parent_id = asyncio.run(_run_rls(_TID, "test:bert", _flow))
    assert geweigerd == "HEEFT_SUBPAKKETTEN"
    assert str(kind_parent) == str(parent_id)  # kind niet geweesd door de element-cascade


@integratie
def test_work_package_zoekfilter_live():
    """De `zoek`-filter (ILIKE op naam) bedient het 'bovenliggend werkpakket'-keuzeveld."""
    from schemas.work_package import WorkPackageCreate
    from services import work_package_service as svc

    async def _flow(s):
        ids = []
        try:
            a = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Zoek Alpha uniek"))
            ids.append(a["id"])
            b = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Zoek Beta uniek"))
            ids.append(b["id"])
            items, _ = await svc.lijst(s, _TID, zoek="alpha uniek")
            return [i["naam"] for i in items]
        finally:
            await _ruim(s, ids)

    namen = asyncio.run(_run_rls(_TID, "test:bert", _flow))
    assert "WP-Zoek Alpha uniek" in namen
    assert "WP-Zoek Beta uniek" not in namen  # ILIKE filtert op naam


@integratie
def test_work_package_rls_isolatie_live():
    from sqlalchemy import text as _text
    from schemas.work_package import WorkPackageCreate
    from services import work_package_service as svc

    async def _maak(s):
        return (await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-RLS")))["id"]

    async def _zicht(s, wid):
        return (await s.execute(_text("SELECT count(*) FROM work_package WHERE id=:i"), {"i": str(wid)})).scalar()

    wid = asyncio.run(_run_rls(_TID, "test:bert", _maak))
    try:
        zicht_b = asyncio.run(_run_rls(_TID_B, "test:bert", lambda s: _zicht(s, wid)))
        zicht_a = asyncio.run(_run_rls(_TID, "test:bert", lambda s: _zicht(s, wid)))
    finally:
        asyncio.run(_run_rls(_TID, "test:bert", lambda s: _ruim(s, [wid])))
    assert zicht_b == 0 and zicht_a == 1


@integratie
def test_work_package_audit_en_geen_engine_live():
    from sqlalchemy import text as _text
    from schemas.work_package import WorkPackageCreate
    from services import work_package_service as svc

    async def _flow(s):
        ids = []
        try:
            wp = await svc.maak_aan(s, _TID, WorkPackageCreate(naam="WP-Audit"))
            ids.append(wp["id"])
            audit = (await s.execute(_text(
                "SELECT count(*) FROM audit_log WHERE entiteit_type='work_package' AND entiteit_id=:i"),
                {"i": str(wp["id"])})).scalar()
            # Geen engine-state: een werkpakket krijgt geen component_profiel.
            profiel = (await s.execute(_text(
                "SELECT count(*) FROM component_profiel WHERE id=:i"), {"i": str(wp["id"])})).scalar()
            return audit, profiel
        finally:
            await _ruim(s, ids)

    audit, profiel = asyncio.run(_run_rls(_TID, "test:bert", _flow))
    assert audit >= 1 and profiel == 0
