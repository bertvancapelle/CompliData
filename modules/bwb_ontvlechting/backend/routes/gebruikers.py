"""HTTP-routes — gebruikersbeheer (ADR-029 Fase 2).

KILARA is de primaire ingang voor gebruikers. `POST /gebruikers` maakt persoon + Keycloak-account
+ koppelrij en geeft het tijdelijk wachtwoord éénmalig terug. RBAC via de `GEBRUIKERSBEHEER`-
entiteit (alleen Beheerder = LAWV). Dunne handlers; logica in de service.
Route-volgorde: lijst (`""`) vóór eventuele dynamische subpaden.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.gebruiker import (
    GebruikerAangemaaktResponse,
    GebruikerAanmakenRequest,
    GebruikerPersoonRead,
)
from services import gebruiker_service as svc

router = APIRouter(prefix="/gebruikers", tags=["bwb:gebruikers"])


@router.get("", response_model=list[GebruikerPersoonRead])
async def lijst_gebruikers(
    limit: int = Query(25, ge=1, le=100),
    after: str | None = Query(None),
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.GEBRUIKERSBEHEER, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Gekoppelde gebruikers binnen de tenant (join koppelrij ↔ persoon), gesorteerd op naam."""
    items, _volgende = await svc.lijst_gebruikers(session, user.tenant_id, limit=limit, after=after)
    return items


@router.post("", response_model=GebruikerAangemaaktResponse, status_code=201)
async def maak_gebruiker(
    body: GebruikerAanmakenRequest,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.GEBRUIKERSBEHEER, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Maak een gebruiker aan (persoon + Keycloak-account + koppeling). Geeft het tijdelijk
    wachtwoord éénmalig terug — beheerder communiceert het, het wordt niet opgeslagen/gelogd."""
    gebruiker, wachtwoord = await svc.maak_gebruiker(
        session, user.tenant_id, naam=body.naam, email=body.email,
        afdeling_id=body.afdeling_id, functietitel=body.functietitel, rol=body.rol,
    )
    return GebruikerAangemaaktResponse(gebruiker=gebruiker, tijdelijk_wachtwoord=wachtwoord)
