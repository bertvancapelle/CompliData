"""Service-laag voor de entiteit Datatype (P5-vervolg, ADR-009).

Kind van Applicatie (1-op-veel), zonder lifecycle. Zelfde tenant-bescherming
als de Applicatie-referentie: RLS (`get_tenant_session`) ÉN expliciete
`tenant_id`-filter. Bij aanmaken wordt de ouder-`Applicatie` tenant-scoped
gevalideerd (hergebruik `applicatie_service.haal_op`) → ouder buiten de tenant
⇒ HTTP 404 `NIET_GEVONDEN` (OP-6, geen lek). `applicatie_id` is immutabel
(niet in Update).
"""
import uuid

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Datatype
from schemas.datatype import DatatypeCreate, DatatypeUpdate
from services import applicatie_service
from services.errors import NietGevonden
from services.pagination import decode_cursor, encode_cursor

_ENTITEIT = "datatype"
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
    applicatie_id: uuid.UUID | None = None,
) -> tuple[list[Datatype], str | None]:
    """Cursor-gepagineerde lijst binnen de tenant, optioneel gefilterd op ouder."""
    limit = max(1, min(limit, _MAX_LIMIT))
    tid = _tenant_uuid(tenant_id)

    stmt = select(Datatype).where(Datatype.tenant_id == tid)
    if applicatie_id is not None:
        stmt = stmt.where(Datatype.applicatie_id == applicatie_id)
    if after:
        cursor_created_at, cursor_id = decode_cursor(after)
        stmt = stmt.where(
            tuple_(Datatype.created_at, Datatype.id) > (cursor_created_at, cursor_id)
        )
    stmt = stmt.order_by(Datatype.created_at, Datatype.id).limit(limit + 1)

    rijen = list((await session.execute(stmt)).scalars().all())
    heeft_meer = len(rijen) > limit
    items = rijen[:limit]
    volgende = encode_cursor(items[-1]) if heeft_meer else None
    return items, volgende


async def haal_op(session: AsyncSession, tenant_id, datatype_id) -> Datatype:
    tid = _tenant_uuid(tenant_id)
    stmt = select(Datatype).where(
        Datatype.id == datatype_id,
        Datatype.tenant_id == tid,
    )
    obj = (await session.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, datatype_id)
    return obj


async def maak_aan(session: AsyncSession, tenant_id, data: DatatypeCreate) -> Datatype:
    tid = _tenant_uuid(tenant_id)
    # Ouder-validatie tenant-scoped — ouder buiten de tenant ⇒ NietGevonden (404).
    await applicatie_service.haal_op(session, tenant_id, data.applicatie_id)
    obj = Datatype(tenant_id=tid, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def werk_bij(
    session: AsyncSession, tenant_id, datatype_id, data: DatatypeUpdate
) -> Datatype:
    obj = await haal_op(session, tenant_id, datatype_id)
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return obj


async def verwijder(session: AsyncSession, tenant_id, datatype_id) -> None:
    obj = await haal_op(session, tenant_id, datatype_id)
    await session.delete(obj)
    await session.commit()
