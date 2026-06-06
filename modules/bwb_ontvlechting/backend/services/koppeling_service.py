"""Service-laag voor de entiteit Koppeling (P5-vervolg, ADR-009).

Twee ouder-relaties naar Applicatie, zonder lifecycle. Beide ouders worden bij
aanmaken tenant-scoped gevalideerd (`applicatie_service.haal_op`) → ontbrekend/
kruis-tenant ⇒ 404 `NIET_GEVONDEN`. `bron ≠ doel` is al op schema-niveau
afgedwongen; de DB-`CHECK ck_koppeling_bron_ne_doel` is backstop: een
`IntegrityError` wordt teruggerold en als `KoppelingConflict` (409) gemeld,
zodat er nooit een rauwe DB-melding lekt. Geen unieke index → geen dubbele-
koppeling-conflict. Ouder-FK's zijn immutabel (niet in Update).
"""
import uuid

from sqlalchemy import select, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Koppeling
from schemas.koppeling import KoppelingCreate, KoppelingUpdate
from services import applicatie_service
from services.errors import KoppelingConflict, NietGevonden
from services.pagination import decode_cursor, encode_cursor

_ENTITEIT = "koppeling"
_STANDAARD_LIMIT = 25
_MAX_LIMIT = 100


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


async def lijst(
    session: AsyncSession,
    tenant_id,
    *,
    limit: int = _STANDAARD_LIMIT,
    after: str | None = None,
    bron_applicatie_id: uuid.UUID | None = None,
    doel_applicatie_id: uuid.UUID | None = None,
) -> tuple[list[Koppeling], str | None]:
    """Cursor-gepagineerde lijst binnen de tenant, optioneel gefilterd op bron/doel."""
    limit = max(1, min(limit, _MAX_LIMIT))
    tid = _tenant_uuid(tenant_id)

    stmt = select(Koppeling).where(Koppeling.tenant_id == tid)
    if bron_applicatie_id is not None:
        stmt = stmt.where(Koppeling.bron_applicatie_id == bron_applicatie_id)
    if doel_applicatie_id is not None:
        stmt = stmt.where(Koppeling.doel_applicatie_id == doel_applicatie_id)
    if after:
        cursor_created_at, cursor_id = decode_cursor(after)
        stmt = stmt.where(
            tuple_(Koppeling.created_at, Koppeling.id) > (cursor_created_at, cursor_id)
        )
    stmt = stmt.order_by(Koppeling.created_at, Koppeling.id).limit(limit + 1)

    rijen = list((await session.execute(stmt)).scalars().all())
    heeft_meer = len(rijen) > limit
    items = rijen[:limit]
    volgende = encode_cursor(items[-1]) if heeft_meer else None
    return items, volgende


async def haal_op(session: AsyncSession, tenant_id, koppeling_id) -> Koppeling:
    tid = _tenant_uuid(tenant_id)
    stmt = select(Koppeling).where(
        Koppeling.id == koppeling_id,
        Koppeling.tenant_id == tid,
    )
    obj = (await session.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, koppeling_id)
    return obj


async def maak_aan(session: AsyncSession, tenant_id, data: KoppelingCreate) -> Koppeling:
    tid = _tenant_uuid(tenant_id)
    # Beide ouders tenant-scoped valideren — ontbrekend/kruis-tenant ⇒ 404.
    await applicatie_service.haal_op(session, tenant_id, data.bron_applicatie_id)
    await applicatie_service.haal_op(session, tenant_id, data.doel_applicatie_id)

    obj = Koppeling(tenant_id=tid, **data.model_dump())
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as exc:
        # Backstop voor de DB-CHECK (bron <> doel); nooit rauwe DB-melding lekken.
        await session.rollback()
        raise KoppelingConflict() from exc
    await session.refresh(obj)
    return obj


async def werk_bij(
    session: AsyncSession, tenant_id, koppeling_id, data: KoppelingUpdate
) -> Koppeling:
    obj = await haal_op(session, tenant_id, koppeling_id)
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return obj


async def verwijder(session: AsyncSession, tenant_id, koppeling_id) -> None:
    obj = await haal_op(session, tenant_id, koppeling_id)
    await session.delete(obj)
    await session.commit()
