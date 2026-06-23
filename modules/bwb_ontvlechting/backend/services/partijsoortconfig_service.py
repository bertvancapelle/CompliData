"""Service-laag — platform-beheer van de partijsoort-catalogus.

Spiegel van `vraagbetekenisconfig_service` op `get_platform_session` (lk_platform), enkel-doel
(geen `dimensie`). Beheert `partijsoort_optie`. Geen hard delete; soft-deactivate via `actief`.
NB: platform-laag — tenant-eigen partijsoort blijft geparkeerd.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import PartijsoortOptie
from schemas.partijsoortconfig import PartijsoortOptieCreate, PartijsoortOptieUpdate
from services.errors import ConfiguratieConflict, NietGevonden


async def lijst(session: AsyncSession) -> list[PartijsoortOptie]:
    stmt = select(PartijsoortOptie).order_by(PartijsoortOptie.volgorde, PartijsoortOptie.id)
    return list((await session.execute(stmt)).scalars().all())


async def _haal(session: AsyncSession, optie_id: int) -> PartijsoortOptie:
    obj = (
        await session.execute(select(PartijsoortOptie).where(PartijsoortOptie.id == optie_id))
    ).scalar_one_or_none()
    if obj is None:
        raise NietGevonden("partijsoort_optie", optie_id)
    return obj


async def voeg_toe(session: AsyncSession, data: PartijsoortOptieCreate) -> PartijsoortOptie:
    """Voeg een optie toe. Duplicaat `optie_sleutel` ⇒ 409. `volgorde` default = max+1."""
    bestaat = (
        await session.execute(
            select(PartijsoortOptie.id).where(PartijsoortOptie.optie_sleutel == data.optie_sleutel)
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise ConfiguratieConflict("Een optie met deze sleutel bestaat al.")

    if data.volgorde is None:
        huidige_max = (await session.execute(select(func.max(PartijsoortOptie.volgorde)))).scalar_one()
        volgorde = 0 if huidige_max is None else huidige_max + 1
    else:
        volgorde = data.volgorde

    obj = PartijsoortOptie(
        optie_sleutel=data.optie_sleutel, label=data.label, volgorde=volgorde, actief=True
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def wijzig(session: AsyncSession, optie_id: int, data: PartijsoortOptieUpdate) -> PartijsoortOptie:
    """Wijzig label / volgorde / actief. Soft-deactivate én reactivate vrij. Onbekend id ⇒ 404."""
    obj = await _haal(session, optie_id)
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return obj
