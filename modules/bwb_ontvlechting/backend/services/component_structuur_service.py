"""Service-laag voor ComponentStructuur (ADR-021 Besluit 6 — Fase B).

Beide componenten tenant-scoped resolven (404); `relatietype` tegen de actieve catalogus-
dimensie `structuurrelatie_type`; self-ref → 422 `ZELFVERWIJZING`; duplicaat → 409
`RELATIE_BESTAAT` (nette app-fout vóór CHECK/UNIQUE). Geen verdere cyclusbewaking (B3).
"""
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import ComponentConfigDimensie, ComponentStructuur
from schemas.component_structuur import ComponentStructuurCreate, ComponentStructuurUpdate
from services import component_service
from services import componentconfig_catalog as catalog
from services.errors import NietGevonden, OngeldigeRegistratie, RegistratieConflict

_ENTITEIT = "component_structuur"


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


async def haal_op(session: AsyncSession, tenant_id, structuur_id) -> ComponentStructuur:
    tid = _tenant_uuid(tenant_id)
    obj = (
        await session.execute(
            select(ComponentStructuur).where(
                ComponentStructuur.id == structuur_id, ComponentStructuur.tenant_id == tid
            )
        )
    ).scalar_one_or_none()
    if obj is None:
        raise NietGevonden(_ENTITEIT, structuur_id)
    return obj


async def _lees(session: AsyncSession, obj: ComponentStructuur) -> dict:
    rel_labels = await catalog.labels(session, ComponentConfigDimensie.structuurrelatie_type)
    return {
        "id": obj.id,
        "component_id": obj.component_id,
        "op_component_id": obj.op_component_id,
        "relatietype": obj.relatietype,
        "relatietype_label": catalog.resolveer_een(obj.relatietype, rel_labels),
        "omschrijving": obj.omschrijving,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }


async def maak_aan(session: AsyncSession, tenant_id, data: ComponentStructuurCreate) -> dict:
    tid = _tenant_uuid(tenant_id)
    if data.component_id == data.op_component_id:
        raise OngeldigeRegistratie(
            "ZELFVERWIJZING", "Een component kan geen structuurrelatie met zichzelf hebben."
        )
    await component_service.haal_op(session, tenant_id, data.component_id)
    await component_service.haal_op(session, tenant_id, data.op_component_id)
    await catalog.valideer_sleutel(session, ComponentConfigDimensie.structuurrelatie_type, data.relatietype)

    bestaat = (
        await session.execute(
            select(ComponentStructuur.id).where(
                ComponentStructuur.tenant_id == tid,
                ComponentStructuur.component_id == data.component_id,
                ComponentStructuur.op_component_id == data.op_component_id,
                ComponentStructuur.relatietype == data.relatietype,
            )
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise RegistratieConflict("RELATIE_BESTAAT", "Deze structuurrelatie bestaat al.")

    obj = ComponentStructuur(
        tenant_id=tid, component_id=data.component_id, op_component_id=data.op_component_id,
        relatietype=data.relatietype, omschrijving=data.omschrijving,
    )
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as exc:  # backstop voor UNIQUE/CHECK
        await session.rollback()
        raise RegistratieConflict("RELATIE_BESTAAT", "Deze structuurrelatie bestaat al.") from exc
    await session.refresh(obj)
    return await _lees(session, obj)


async def werk_bij(session: AsyncSession, tenant_id, structuur_id, data: ComponentStructuurUpdate) -> dict:
    obj = await haal_op(session, tenant_id, structuur_id)
    velden = data.model_dump(exclude_unset=True)
    if velden.get("relatietype") is not None:
        await catalog.valideer_sleutel(session, ComponentConfigDimensie.structuurrelatie_type, velden["relatietype"])
    for veld, waarde in velden.items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return await _lees(session, obj)


async def verwijder(session: AsyncSession, tenant_id, structuur_id) -> None:
    obj = await haal_op(session, tenant_id, structuur_id)
    await session.delete(obj)
    await session.commit()
