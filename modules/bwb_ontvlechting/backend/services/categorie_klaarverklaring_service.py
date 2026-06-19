"""Service-laag — categorie-klaarverklaring (ADR-027 slice 1).

Niet-scorende verklaring "checklist-categorie X op component Y is beoordeeld en afgehandeld",
als eigen tenant-scoped registratie-feit (`CategorieKlaarverklaring`). Eén levende verklaring per
(component, categorie_nr); statushandelingen (klaar↔open) vereisen een reden en herstempelen
`verklaard_door`/`verklaard_op` server-side. Tenant-scoped (RLS + expliciet `tenant_id`-filter).

Validatie: component bestaat binnen de tenant (→ 404), categorie_nr bestaat voor het componenttype
(→ 422 `ONGELDIGE_CATEGORIE`), dubbel paar → 409 `KLAARVERKLARING_BESTAAT_AL`. Lege reden wordt al
in het schema afgevangen (422 native).

Puur registratief — RAAKT DE ENGINE NOOIT: importeert géén `lifecycle_service`/`herbereken_lifecycle`/
`bepaal_lifecycle`/`ComponentProfiel`/`Blokkade`/`Checklistscore` en schrijft niets in lifecycle-/
score-/blokkade-state. (`ChecklistVraag` wordt alleen gelezen om het categorie_nr te valideren —
dat is de catalogus, niet de engine.)
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant_context import huidige_actor
from models.models import CategorieKlaarverklaring, ChecklistVraag, Component, KlaarverklaringStatus
from schemas.categorie_klaarverklaring import KlaarverklaringCreate, KlaarverklaringStatusWijzig
from services.errors import NietGevonden, OngeldigeRegistratie, RegistratieConflict

_ENTITEIT = "categorie_klaarverklaring"


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


def _stempel() -> tuple[str | None, datetime]:
    """Server-side actor + tijdstip (registratie, niet door client aanleverbaar)."""
    actor_sub, actor_email = huidige_actor()
    return (actor_email or actor_sub or None, datetime.now(timezone.utc))


async def _componenttype(session: AsyncSession, tid: uuid.UUID, component_id) -> str:
    """Componenttype van een component binnen de tenant; niet gevonden ⇒ 404 (geen lek)."""
    ct = (
        await session.execute(
            select(Component.componenttype).where(
                Component.id == component_id, Component.tenant_id == tid
            )
        )
    ).scalar_one_or_none()
    if ct is None:
        raise NietGevonden("component", component_id)
    return ct


async def _valideer_categorie(session: AsyncSession, tid: uuid.UUID, componenttype: str, categorie_nr: int) -> None:
    aantal = (
        await session.execute(
            select(func.count())
            .select_from(ChecklistVraag)
            .where(
                ChecklistVraag.tenant_id == tid,
                ChecklistVraag.componenttype == componenttype,
                ChecklistVraag.categorie_nr == categorie_nr,
            )
        )
    ).scalar_one()
    if not aantal:
        raise OngeldigeRegistratie(
            "ONGELDIGE_CATEGORIE",
            f"Categorie {categorie_nr} bestaat niet voor dit componenttype.",
        )


async def maak_aan(session: AsyncSession, tenant_id, data: KlaarverklaringCreate) -> CategorieKlaarverklaring:
    tid = _tenant_uuid(tenant_id)
    componenttype = await _componenttype(session, tid, data.component_id)
    await _valideer_categorie(session, tid, componenttype, data.categorie_nr)
    door, op = _stempel()
    obj = CategorieKlaarverklaring(
        tenant_id=tid,
        component_id=data.component_id,
        categorie_nr=data.categorie_nr,
        status=KlaarverklaringStatus.klaar,
        reden=data.reden,
        verklaard_door=door,
        verklaard_op=op,
    )
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise RegistratieConflict(
            "KLAARVERKLARING_BESTAAT_AL",
            "Er bestaat al een klaarverklaring voor deze categorie; gebruik de statuswijziging.",
        )
    await session.refresh(obj)
    return obj


async def haal_op(session: AsyncSession, tenant_id, klaarverklaring_id) -> CategorieKlaarverklaring:
    tid = _tenant_uuid(tenant_id)
    obj = (
        await session.execute(
            select(CategorieKlaarverklaring).where(
                CategorieKlaarverklaring.id == klaarverklaring_id,
                CategorieKlaarverklaring.tenant_id == tid,
            )
        )
    ).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, klaarverklaring_id)
    return obj


async def wijzig_status(
    session: AsyncSession, tenant_id, klaarverklaring_id, data: KlaarverklaringStatusWijzig
) -> CategorieKlaarverklaring:
    """Symmetrisch klaar↔open; nieuwe reden verplicht (schema), herstempelt wie/wanneer."""
    obj = await haal_op(session, tenant_id, klaarverklaring_id)
    door, op = _stempel()
    obj.status = KlaarverklaringStatus(data.status)
    obj.reden = data.reden
    obj.verklaard_door = door
    obj.verklaard_op = op
    await session.commit()
    await session.refresh(obj)
    return obj


async def lijst(
    session: AsyncSession, tenant_id, *, component_id=None, categorie_nr=None
) -> list[CategorieKlaarverklaring]:
    """Tenant-scoped (RLS + expliciet filter); optioneel per component en/of (component, categorie_nr).

    Bewust géén keyset-paginering: een begrensde sub-lijst per component (analoog aan andere
    afgeleide overzichten), niet de generieke lijst-norm.
    """
    tid = _tenant_uuid(tenant_id)
    stmt = select(CategorieKlaarverklaring).where(CategorieKlaarverklaring.tenant_id == tid)
    if component_id is not None:
        stmt = stmt.where(CategorieKlaarverklaring.component_id == component_id)
    if categorie_nr is not None:
        stmt = stmt.where(CategorieKlaarverklaring.categorie_nr == categorie_nr)
    stmt = stmt.order_by(CategorieKlaarverklaring.component_id, CategorieKlaarverklaring.categorie_nr)
    return list((await session.execute(stmt)).scalars().all())
