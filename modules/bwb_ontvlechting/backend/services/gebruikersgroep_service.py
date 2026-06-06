"""Service-laag voor de entiteit Gebruikersgroep (P5-vervolg, ADR-009).

Kind van Applicatie (1-op-veel), zonder lifecycle. Identiek patroon aan
`datatype_service`: RLS + expliciete `tenant_id`-filter, ouder-validatie
tenant-scoped bij aanmaken (ouder buiten tenant ⇒ 404 `NIET_GEVONDEN`),
`applicatie_id` immutabel.
"""
import uuid

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Gebruikersgroep
from schemas.gebruikersgroep import GebruikersgroepCreate, GebruikersgroepUpdate
from services import applicatie_service
from services.errors import NietGevonden
from services.pagination import decode_cursor, encode_cursor

_ENTITEIT = "gebruikersgroep"
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
) -> tuple[list[Gebruikersgroep], str | None]:
    """Cursor-gepagineerde lijst binnen de tenant, optioneel gefilterd op ouder."""
    limit = max(1, min(limit, _MAX_LIMIT))
    tid = _tenant_uuid(tenant_id)

    stmt = select(Gebruikersgroep).where(Gebruikersgroep.tenant_id == tid)
    if applicatie_id is not None:
        stmt = stmt.where(Gebruikersgroep.applicatie_id == applicatie_id)
    if after:
        cursor_created_at, cursor_id = decode_cursor(after)
        stmt = stmt.where(
            tuple_(Gebruikersgroep.created_at, Gebruikersgroep.id)
            > (cursor_created_at, cursor_id)
        )
    stmt = stmt.order_by(Gebruikersgroep.created_at, Gebruikersgroep.id).limit(limit + 1)

    rijen = list((await session.execute(stmt)).scalars().all())
    heeft_meer = len(rijen) > limit
    items = rijen[:limit]
    volgende = encode_cursor(items[-1]) if heeft_meer else None
    return items, volgende


async def haal_op(session: AsyncSession, tenant_id, gebruikersgroep_id) -> Gebruikersgroep:
    tid = _tenant_uuid(tenant_id)
    stmt = select(Gebruikersgroep).where(
        Gebruikersgroep.id == gebruikersgroep_id,
        Gebruikersgroep.tenant_id == tid,
    )
    obj = (await session.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, gebruikersgroep_id)
    return obj


async def maak_aan(
    session: AsyncSession, tenant_id, data: GebruikersgroepCreate
) -> Gebruikersgroep:
    tid = _tenant_uuid(tenant_id)
    # Ouder-validatie tenant-scoped — ouder buiten de tenant ⇒ NietGevonden (404).
    await applicatie_service.haal_op(session, tenant_id, data.applicatie_id)
    obj = Gebruikersgroep(tenant_id=tid, **data.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def werk_bij(
    session: AsyncSession, tenant_id, gebruikersgroep_id, data: GebruikersgroepUpdate
) -> Gebruikersgroep:
    obj = await haal_op(session, tenant_id, gebruikersgroep_id)
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return obj


async def verwijder(session: AsyncSession, tenant_id, gebruikersgroep_id) -> None:
    obj = await haal_op(session, tenant_id, gebruikersgroep_id)
    await session.delete(obj)
    await session.commit()
