"""Catalogus-lookup/-validatie voor de checklistvraag-betekenissen (ADR-023 Fase F / F-3).

Spiegel van `relatiekenmerk_catalog`, maar voor de platform-brede catalogus
`vraagbetekenis_optie` (één doel, geen dimensie). De tenant-sessie (`cd_app`) mag deze
catalogus LEZEN (SELECT-grant) — voor het betekenis-keuzeveld én de validatie van een
toegekende betekenis. Valideren tegen de **actieve** opties; uitlezen resolvet ook
gedeactiveerde sleutels (historie). Voedt de engine NIET.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import VraagBetekenisOptie
from services.errors import OngeldigeRegistratie


async def actieve_opties(session: AsyncSession) -> list[dict]:
    """Actieve betekenissen (keuzeveld), gesorteerd op `volgorde`. Alleen-actief."""
    rijen = (
        await session.execute(
            select(
                VraagBetekenisOptie.optie_sleutel,
                VraagBetekenisOptie.label,
                VraagBetekenisOptie.volgorde,
            )
            .where(VraagBetekenisOptie.actief.is_(True))
            .order_by(VraagBetekenisOptie.volgorde, VraagBetekenisOptie.id)
        )
    ).all()
    return [
        {"optie_sleutel": r.optie_sleutel, "label": r.label, "volgorde": r.volgorde}
        for r in rijen
    ]


async def actieve_sleutels(session: AsyncSession) -> set[str]:
    return {
        r.optie_sleutel
        for r in (
            await session.execute(
                select(VraagBetekenisOptie.optie_sleutel).where(
                    VraagBetekenisOptie.actief.is_(True)
                )
            )
        ).all()
    }


async def valideer_sleutel(session: AsyncSession, sleutel: str) -> None:
    """Weiger een onbekende/inactieve betekenis ⇒ 422 `ONGELDIGE_OPTIE`."""
    if sleutel in await actieve_sleutels(session):
        return
    raise OngeldigeRegistratie(
        "ONGELDIGE_OPTIE",
        f"Onbekende of inactieve betekenis: '{sleutel}'.",
    )
