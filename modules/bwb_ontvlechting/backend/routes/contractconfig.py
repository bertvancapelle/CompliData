"""Platform-beheer-endpoints — contract-classificatie-catalogus (ADR-020 Besluit 6/7,
ADR-012 Addendum B).

Geautoriseerd via `vereist_platform_permissie(CONTRACTCONFIG, …)` (platform-rollen) op
`get_platform_session` (cd_platform, géén tenant-/RLS-context). Beheert referentiedata
(`contractconfig_optie`); raakt de tenant-data (`contract*`) NIET.

Foutgedrag: 401 · 403 `ONVOLDOENDE_RECHTEN` · 404 `NIET_GEVONDEN` · 409
`CONFIGURATIE_CONFLICT` (duplicaat) · 422 (Pydantic). Géén DELETE (Addendum B Besluit 3).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.platform_rbac import PlatformEntiteit
from app.core.rbac import Actie
from app.middleware.authz import vereist_platform_permissie
from app.middleware.tenant import get_platform_session
from models.models import ContractConfigDimensie
from schemas.contractconfig import (
    ContractConfigOptieCreate,
    ContractConfigOptieRead,
    ContractConfigOptieUpdate,
)
from services import contractconfig_service as svc

router = APIRouter(prefix="/platform/contractconfig", tags=["platform:contractconfig"])

_LEZEN = vereist_platform_permissie(PlatformEntiteit.CONTRACTCONFIG, Actie.LEZEN)
_AANMAKEN = vereist_platform_permissie(PlatformEntiteit.CONTRACTCONFIG, Actie.AANMAKEN)
_WIJZIGEN = vereist_platform_permissie(PlatformEntiteit.CONTRACTCONFIG, Actie.WIJZIGEN)


@router.get("", response_model=list[ContractConfigOptieRead])
async def lijst(
    dimensie: ContractConfigDimensie | None = Query(None),
    _user=Depends(_LEZEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Alle catalogus-opties (incl. inactieve), optioneel per `?dimensie=`."""
    return await svc.lijst(session, dimensie.value if dimensie else None)


@router.post("", response_model=ContractConfigOptieRead, status_code=201)
async def voeg_toe(
    body: ContractConfigOptieCreate,
    _user=Depends(_AANMAKEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Voeg een optie toe; duplicaat `(dimensie, optie_sleutel)` ⇒ 409."""
    return await svc.voeg_toe(session, body)


@router.patch("/{optie_id}", response_model=ContractConfigOptieRead)
async def wijzig(
    optie_id: int,
    body: ContractConfigOptieUpdate,
    _user=Depends(_WIJZIGEN),
    session: AsyncSession = Depends(get_platform_session),
):
    """Wijzig label/volgorde/actief; deactiveren én reactiveren toegestaan (soft-deactivate)."""
    return await svc.wijzig(session, optie_id, body)
