"""Service-laag — platform-beheer van de vraagbetekenis-catalogus.

Spiegel van `relatiekenmerkconfig_service` op `get_platform_session` (lk_platform), maar
enkel-doel (geen `dimensie`). Beheert `vraagbetekenis_optie`. Geen hard delete (geen endpoint +
ontbrekende DELETE-grant = dubbele borging); soft-deactivate via `actief`. Geen beschermde sleutel.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import VraagBetekenisOptie
from schemas.vraagbetekenisconfig import VraagBetekenisOptieCreate, VraagBetekenisOptieUpdate
from services.errors import ConfiguratieConflict, NietGevonden


async def lijst(session: AsyncSession) -> list[VraagBetekenisOptie]:
    stmt = select(VraagBetekenisOptie).order_by(VraagBetekenisOptie.volgorde, VraagBetekenisOptie.id)
    return list((await session.execute(stmt)).scalars().all())


async def _haal(session: AsyncSession, optie_id: int) -> VraagBetekenisOptie:
    obj = (
        await session.execute(select(VraagBetekenisOptie).where(VraagBetekenisOptie.id == optie_id))
    ).scalar_one_or_none()
    if obj is None:
        raise NietGevonden("vraagbetekenis_optie", optie_id)
    return obj


async def voeg_toe(session: AsyncSession, data: VraagBetekenisOptieCreate) -> VraagBetekenisOptie:
    """Voeg een optie toe. Duplicaat `optie_sleutel` ⇒ 409. `volgorde` default = max+1."""
    bestaat = (
        await session.execute(
            select(VraagBetekenisOptie.id).where(VraagBetekenisOptie.optie_sleutel == data.optie_sleutel)
        )
    ).scalar_one_or_none()
    if bestaat is not None:
        raise ConfiguratieConflict("Een optie met deze sleutel bestaat al.")

    if data.volgorde is None:
        huidige_max = (await session.execute(select(func.max(VraagBetekenisOptie.volgorde)))).scalar_one()
        volgorde = 0 if huidige_max is None else huidige_max + 1
    else:
        volgorde = data.volgorde

    obj = VraagBetekenisOptie(
        optie_sleutel=data.optie_sleutel, label=data.label, volgorde=volgorde, actief=True
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def wijzig(
    session: AsyncSession, optie_id: int, data: VraagBetekenisOptieUpdate
) -> VraagBetekenisOptie:
    """Wijzig label / volgorde / actief. Soft-deactivate én reactivate vrij. Onbekend id ⇒ 404."""
    obj = await _haal(session, optie_id)
    for veld, waarde in data.model_dump(exclude_unset=True).items():
        setattr(obj, veld, waarde)
    await session.commit()
    await session.refresh(obj)
    return obj
