"""Platform-beheer-endpoints — partijsoort-catalogus (platform-laag).

Geautoriseerd via `vereist_platform_permissie(PARTIJSOORTCONFIG, …)` (platform-rollen) op
`get_platform_session` (cd_platform). Beheert `partijsoort_optie`; raakt tenant-data NIET.
Géén DELETE (soft-deactivate via `actief`). Spiegel van `routes/vraagbetekenisconfig`.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.platform_rbac import PlatformEntiteit
from app.core.rbac import Actie
from app.middleware.authz import vereist_platform_permissie
from app.middleware.tenant import get_platform_session
from schemas.partijsoortconfig import (
    PartijsoortOptieCreate,
    PartijsoortOptieRead,
    PartijsoortOptieUpdate,
)
from services import partijsoortconfig_service as svc

router = APIRouter(prefix="/platform/partijsoortconfig", tags=["platform:partijsoortconfig"])

_LEZEN = vereist_platform_permissie(PlatformEntiteit.PARTIJSOORTCONFIG, Actie.LEZEN)
_AANMAKEN = vereist_platform_permissie(PlatformEntiteit.PARTIJSOORTCONFIG, Actie.AANMAKEN)
_WIJZIGEN = vereist_platform_permissie(PlatformEntiteit.PARTIJSOORTCONFIG, Actie.WIJZIGEN)


@router.get("", response_model=list[PartijsoortOptieRead])
async def lijst(_user=Depends(_LEZEN), session: AsyncSession = Depends(get_platform_session)):
    """Alle partijsoort-opties (incl. inactieve)."""
    return await svc.lijst(session)


@router.post("", response_model=PartijsoortOptieRead, status_code=201)
async def voeg_toe(
    body: PartijsoortOptieCreate,
    _user=Depends(_AANMAKEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Voeg een partijsoort-optie toe; duplicaat `optie_sleutel` ⇒ 409."""
    return await svc.voeg_toe(session, body)


@router.patch("/{optie_id}", response_model=PartijsoortOptieRead)
async def wijzig(
    optie_id: int,
    body: PartijsoortOptieUpdate,
    _user=Depends(_WIJZIGEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Wijzig label/volgorde/actief; deactiveren én reactiveren vrij. Onbekend id ⇒ 404."""
    return await svc.wijzig(session, optie_id, body)
