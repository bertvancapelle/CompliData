"""Platform-beheer-endpoints — vraagbetekenis-catalogus.

Geautoriseerd via `vereist_platform_permissie(VRAAGBETEKENISCONFIG, …)` (platform-rollen) op
`get_platform_session` (cd_platform). Beheert `vraagbetekenis_optie`; raakt tenant-data NIET.
Géén DELETE (soft-deactivate via `actief`). Spiegel van `routes/relatiekenmerkconfig`.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.platform_rbac import PlatformEntiteit
from app.core.rbac import Actie
from app.middleware.authz import vereist_platform_permissie
from app.middleware.tenant import get_platform_session
from schemas.vraagbetekenisconfig import (
    VraagBetekenisOptieCreate,
    VraagBetekenisOptieRead,
    VraagBetekenisOptieUpdate,
)
from services import vraagbetekenisconfig_service as svc

router = APIRouter(prefix="/platform/vraagbetekenisconfig", tags=["platform:vraagbetekenisconfig"])

_LEZEN = vereist_platform_permissie(PlatformEntiteit.VRAAGBETEKENISCONFIG, Actie.LEZEN)
_AANMAKEN = vereist_platform_permissie(PlatformEntiteit.VRAAGBETEKENISCONFIG, Actie.AANMAKEN)
_WIJZIGEN = vereist_platform_permissie(PlatformEntiteit.VRAAGBETEKENISCONFIG, Actie.WIJZIGEN)


@router.get("", response_model=list[VraagBetekenisOptieRead])
async def lijst(_user=Depends(_LEZEN), session: AsyncSession = Depends(get_platform_session)):
    """Alle betekenis-opties (incl. inactieve)."""
    return await svc.lijst(session)


@router.post("", response_model=VraagBetekenisOptieRead, status_code=201)
async def voeg_toe(
    body: VraagBetekenisOptieCreate,
    _user=Depends(_AANMAKEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Voeg een betekenis-optie toe; duplicaat `optie_sleutel` ⇒ 409."""
    return await svc.voeg_toe(session, body)


@router.patch("/{optie_id}", response_model=VraagBetekenisOptieRead)
async def wijzig(
    optie_id: int,
    body: VraagBetekenisOptieUpdate,
    _user=Depends(_WIJZIGEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Wijzig label/volgorde/actief; deactiveren én reactiveren vrij. Onbekend id ⇒ 404."""
    return await svc.wijzig(session, optie_id, body)
