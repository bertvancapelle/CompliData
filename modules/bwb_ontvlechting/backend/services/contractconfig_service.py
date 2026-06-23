"""Service-laag — platform-beheer van de contract-classificatie-catalogus
(ADR-020 Besluit 6, ADR-012 Addendum B).

Draait op `get_platform_session` (lk_platform) — platform-brede referentiedata,
géén tenant-/RLS-context. Raakt de tenant-data (`contract*`) NIET; de tenant-leeszijde
(CD041) resolvet óók inactieve sleutels naar hun label, dus soft-deactiveren verweest
niets. Geen hard delete (Addendum B + ontbrekende DB-grant — dubbele borging).
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import ContractConfigDimensie, ContractConfigOptie
from schemas.contractconfig import ContractConfigOptieCreate, ContractConfigOptieUpdate
from services.errors import ConfiguratieConflict, NietGevonden


async def lijst(session: AsyncSession, dimensie: str | None = None) -> list[ContractConfigOptie]:
    """Alle opties (incl. inactieve), optioneel gefilterd per dimensie; gesorteerd
    op (dimensie, volgorde, id)."""
    stmt = select(ContractConfigOptie)
    if dimensie:
        stmt = stmt.where(ContractConfigOptie.dimensie == ContractConfigDimensie(dimensie))
    stmt = stmt.order_by(
        ContractConfigOptie.dimensie, ContractConfigOptie.volgorde, ContractConfigOptie.id
    )
    return list((await session.execute(stmt)).scalars().all())


async def _haal(session: AsyncSession, optie_id: int) -> ContractConfigOptie:
    obj = (
        await session.execute(
            select(ContractConfigOptie).where(ContractConfigOptie.id == optie_id)
        )
    ).scalar_one_or_none()
    if obj is None:
        raise NietGevonden("contractconfig_optie", optie_id)
    return obj


async def voeg_toe(session: AsyncSession, data: ContractConfigOptieCreate) -> ContractConfigOptie:
    """Voeg een optie toe. Duplicaat `(dimensie, optie_sleutel)` ⇒ 409 (nette app-fout
    vóór het UNIQUE-constraint). `volgorde` default = max(volgorde)+1 binnen de dimensie."""
    bestaat = (
        await session.execute(
            select(ContractConfigOptie.id).where(
                ContractConfigOptie.dimensie == data.dimensie,
                ContractConfigOptie.optie_sleutel == data.optie_sleutel,
            )
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise ConfiguratieConflict(
            "Een optie met deze sleutel bestaat al in deze dimensie."
        )

    if data.volgorde is None:
        huidige_max = (
            await session.execute(
                select(func.max(ContractConfigOptie.volgorde)).where(
                    ContractConfigOptie.dimensie == data.dimensie
                )
            )
        ).scalar_one()
        volgorde = 0 if huidige_max is None else huidige_max + 1
    else:
        volgorde = data.volgorde

    obj = ContractConfigOptie(
        dimensie=data.dimensie,
        optie_sleutel=data.optie_sleutel,
        label=data.label,
        volgorde=volgorde,
        actief=True,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def wijzig(
    session: AsyncSession, optie_id: int, data: ContractConfigOptieUpdate
) -> ContractConfigOptie:
    """Wijzig label / volgorde / actief. Deactiveren én reactiveren zijn altijd toegestaan
    (soft-deactivate-ontwerp, Besluit 6 — geen orphan-blokkade). Onbekend id ⇒ 404."""
    obj = await _haal(session, optie_id)
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return obj
