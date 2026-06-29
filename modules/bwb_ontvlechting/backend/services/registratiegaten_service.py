"""Service — Signalering registratiegaten (ADR-035, Slice 1). Puur read-only afgeleid.

Twee KRITIEKE component-signalen (Slice 1, n≥2):
- ``component_zonder_eigenaar``        — ``component.eigenaar_organisatie_id IS NULL``
- ``component_zonder_verantwoordelijke`` — geen ``roltoewijzing`` met ``object_id == component``

Engine-invariant (machine-geborgd via de offline import-afwezigheidstest): bewust GEEN import van
``lifecycle_service`` / ``herbereken_lifecycle`` / ``bepaal_lifecycle`` / ``ComponentProfiel`` /
``Blokkade`` / ``Checklistscore``. ``lifecycle_status`` (woont op de engine-tabel
``component_profiel``) wordt engine-veilig gelezen via een lichtgewicht ``table()/column()``-handle
i.p.v. de ORM-klasse (zoals de Landschapskaart). Geen mutatie — uitsluitend SELECT; RLS scoopt op
de tenant (dubbele bescherming met de expliciete ``tenant_id``-filter).
"""
import uuid

from sqlalchemy import and_, column, exists, select, table
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Component, Roltoewijzing

# Lichtgewicht handle op de engine-tabel (shared-PK: component_profiel.id == component.id) — leest
# lifecycle_status zonder ComponentProfiel te importeren, zodat de engine-borging groen blijft.
_profiel = table("component_profiel", column("id"), column("tenant_id"), column("lifecycle_status"))

_SIG_EIGENAAR = "component_zonder_eigenaar"
_SIG_VERANTWOORDELIJKE = "component_zonder_verantwoordelijke"
_KRITIEK = "kritiek"


def _tenant_uuid(tenant_id) -> uuid.UUID:
    return tenant_id if isinstance(tenant_id, uuid.UUID) else uuid.UUID(str(tenant_id))


def _lc(val) -> str | None:
    if val is None:
        return None
    return val.value if hasattr(val, "value") else str(val)


def _basis_select(tid: uuid.UUID):
    """Component + lifecycle_status (LEFT JOIN op de profiel-handle), tenant-gescoopt, op naam."""
    return (
        select(Component.id, Component.naam, _profiel.c.lifecycle_status)
        .outerjoin(_profiel, and_(_profiel.c.id == Component.id, _profiel.c.tenant_id == tid))
        .where(Component.tenant_id == tid)
        .order_by(Component.naam.asc(), Component.id.asc())
    )


def _item(r, signaal: str) -> dict:
    return {
        "id": r.id, "naam": r.naam, "lifecycle_status": _lc(r.lifecycle_status),
        "signaal": signaal, "niveau": _KRITIEK,
    }


async def component_zonder_eigenaar(session: AsyncSession, tenant_id) -> list[dict]:
    """Componenten zonder ``eigenaar_organisatie_id`` (IS NULL). Inclusief kale types. Read-only."""
    tid = _tenant_uuid(tenant_id)
    stmt = _basis_select(tid).where(Component.eigenaar_organisatie_id.is_(None))
    rijen = (await session.execute(stmt)).all()
    return [_item(r, _SIG_EIGENAAR) for r in rijen]


async def component_zonder_verantwoordelijke(session: AsyncSession, tenant_id) -> list[dict]:
    """Componenten zonder enige roltoewijzing (geen verantwoordelijke partij). Read-only."""
    tid = _tenant_uuid(tenant_id)
    geen_rol = ~exists(
        select(Roltoewijzing.id).where(
            Roltoewijzing.tenant_id == tid, Roltoewijzing.object_id == Component.id,
        )
    )
    stmt = _basis_select(tid).where(geen_rol)
    rijen = (await session.execute(stmt)).all()
    return [_item(r, _SIG_VERANTWOORDELIJKE) for r in rijen]


async def badge_voor_component(session: AsyncSession, tenant_id, component_id: uuid.UUID) -> dict:
    """Badge-info voor één component (Slice 1: de twee kritieke component-signalen). Read-only.

    Terug: ``{signalen: list[str], kritiek: int, aandacht: int}``. Een component buiten de tenant
    (of onbestaand) levert een lege badge (geen lek)."""
    tid = _tenant_uuid(tenant_id)
    bestaat = (
        await session.execute(
            select(Component.id).where(Component.tenant_id == tid, Component.id == component_id)
        )
    ).first() is not None
    if not bestaat:
        return {"signalen": [], "kritiek": 0, "aandacht": 0}

    geen_eigenaar = (
        await session.execute(
            select(Component.id).where(
                Component.tenant_id == tid,
                Component.id == component_id,
                Component.eigenaar_organisatie_id.is_(None),
            )
        )
    ).first() is not None
    geen_rol = (
        await session.execute(
            select(Roltoewijzing.id).where(
                Roltoewijzing.tenant_id == tid, Roltoewijzing.object_id == component_id,
            )
        )
    ).first() is None

    signalen: list[str] = []
    if geen_eigenaar:
        signalen.append(_SIG_EIGENAAR)
    if geen_rol:
        signalen.append(_SIG_VERANTWOORDELIJKE)
    return {"signalen": signalen, "kritiek": len(signalen), "aandacht": 0}
