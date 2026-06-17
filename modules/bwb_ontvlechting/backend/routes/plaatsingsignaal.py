"""HTTP-routes — consistentie-signalering technische plaatsing (ADR-023 Fase F / F-3 stap 2).

Read-only signalenlijst over alle componenten met een plaatsings-attentiepunt, geguard op
`vereist_permissie(Entiteit.ARCHITECTUUR, Actie.LEZEN)` (zelfde tenant-brede inzicht-laag
als het architectuuroverzicht — geen nieuwe entiteit). Geen schema/migratie; engine
onaangeroerd. Bewust geen paginering: het is een afgeleid, begrensd attentie-overzicht dat
in z'n geheel te beoordelen hoort.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.plaatsingsignaal import PlaatsingSignaalRead
from services import plaatsingsignaal_service as svc

router = APIRouter(prefix="/signalen", tags=["bwb:signalen"])


@router.get("/plaatsing", response_model=list[PlaatsingSignaalRead])
async def lijst_plaatsingsignalen(
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.ARCHITECTUUR, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Alle componenten met een technische-plaatsing-signaal (+ signaaltype + reden)."""
    return await svc.lijst(session, user.tenant_id)
