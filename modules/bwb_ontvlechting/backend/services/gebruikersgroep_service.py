"""Service-laag voor de entiteit Gebruikersgroep (P5-vervolg, ADR-009).

Kind van Applicatie (1-op-veel), zonder lifecycle. Identiek patroon aan
`datatype_service`: RLS + expliciete `tenant_id`-filter, ouder-validatie
tenant-scoped bij aanmaken (ouder buiten tenant ⇒ 404 `NIET_GEVONDEN`),
`applicatie_id` immutabel.
"""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Gebruikersgroep
from schemas.gebruikersgroep import GebruikersgroepCreate, GebruikersgroepUpdate
from services import applicatie_service
from services.errors import NietGevonden
from services.pagination import (
    decode_sort_cursor_nullable,
    encode_sort_cursor_nullable,
    keyset_order_by_nulls_last,
    keyset_seek_nulls_last,
)

_ENTITEIT = "gebruikersgroep"
_STANDAARD_LIMIT = 25
_MAX_LIMIT = 100

# Default-sortering = exact het pre-CD020-gedrag (created_at oplopend).
_STANDAARD_SORT = "created_at"
_STANDAARD_ORDER = "asc"

# Allowlist-kolommen (ADR-017 B2) — single source naast `GebruikersgroepSorteerveld`.
_SORTEERBARE_KOLOMMEN = {
    "created_at": Gebruikersgroep.created_at,
    "organisatie": Gebruikersgroep.organisatie,
    "afdeling": Gebruikersgroep.afdeling,
    "aantal_gebruikers": Gebruikersgroep.aantal_gebruikers,
}
_WAARDE_PARSERS = {
    "created_at": datetime.fromisoformat,
    "organisatie": str,
    "afdeling": str,
    "aantal_gebruikers": int,
}


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


async def lijst(
    session: AsyncSession,
    tenant_id,
    *,
    limit: int = _STANDAARD_LIMIT,
    after: str | None = None,
    applicatie_id: uuid.UUID | None = None,
    sort: str = _STANDAARD_SORT,
    order: str = _STANDAARD_ORDER,
) -> tuple[list[Gebruikersgroep], str | None]:
    """Server-side sorteerbare keyset-lijst binnen de tenant (ADR-017 + CD020).

    Default (geen `sort`/`order`) = exact het pre-CD020-gedrag (`created_at`
    oplopend). Uniform NULLS-LAST-pad (CD016); `Gebruikersgroep.id` = tiebreaker.
    Cursor die niet bij `sort`/`order` past ⇒ `ValueError` (route ⇒ 400).
    """
    limit = max(1, min(limit, _MAX_LIMIT))
    tid = _tenant_uuid(tenant_id)

    if sort not in _SORTEERBARE_KOLOMMEN:
        raise ValueError(f"onbekend sorteerveld: {sort}")
    if order not in (_STANDAARD_ORDER, "desc"):
        raise ValueError(f"onbekende sorteerrichting: {order}")
    kolom = _SORTEERBARE_KOLOMMEN[sort]

    stmt = select(Gebruikersgroep).where(Gebruikersgroep.tenant_id == tid)
    if applicatie_id is not None:
        stmt = stmt.where(Gebruikersgroep.applicatie_id == applicatie_id)
    if after:
        c_sort, c_order, c_is_null, c_waarde_str, c_id = decode_sort_cursor_nullable(after)
        if c_sort != sort or c_order != order:
            raise ValueError("cursor past niet bij de actieve sortering")
        c_waarde = None if c_is_null else _WAARDE_PARSERS[sort](c_waarde_str)
        stmt = stmt.where(
            keyset_seek_nulls_last(
                kolom, Gebruikersgroep.id, order=order, is_null=c_is_null,
                waarde=c_waarde, cursor_id=c_id,
            )
        )
    stmt = stmt.order_by(
        *keyset_order_by_nulls_last(kolom, Gebruikersgroep.id, order)
    ).limit(limit + 1)

    rijen = list((await session.execute(stmt)).scalars().all())
    heeft_meer = len(rijen) > limit
    items = rijen[:limit]
    volgende = (
        encode_sort_cursor_nullable(
            sort=sort, order=order, waarde=getattr(items[-1], kolom.key), id=items[-1].id
        )
        if heeft_meer
        else None
    )
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
