"""HTTP-routes — opgeslagen & deelbare Impact-verkenner-views (ADR-033 slice 2).

Eigen registratie-feit → eigen routebestand (`/impact-views`). RBAC via de eigen entiteit
`IMPACT_VIEW` (Viewer/Auditor L · Medewerker/Beheerder LAWV). De fijnere "alleen de maker
muteert"-regel + privé-zichtbaarheid leven in de service (no-leak-404). Dunne handlers.

Route-volgorde: lijst/aanmaken (`""`) vóór de dynamische `/{view_id}`.
"""
import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.impact_view import ImpactViewCreate, ImpactViewRead, ImpactViewUpdate
from services import impact_view_service as svc

router = APIRouter(prefix="/impact-views", tags=["bwb:impact_view"])


@router.get("", response_model=list[ImpactViewRead])
async def lijst_views(
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.IMPACT_VIEW, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Eigen views + gedeelde views van anderen (binnen de tenant)."""
    return await svc.lijst(session, user.tenant_id)


@router.post("", response_model=ImpactViewRead, status_code=201)
async def maak_view(
    body: ImpactViewCreate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.IMPACT_VIEW, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.maak_aan(session, user.tenant_id, body)


@router.get("/{view_id}", response_model=ImpactViewRead)
async def haal_view(
    view_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.IMPACT_VIEW, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Eén view; andermans privé-view ⇒ 404 (no-leak)."""
    return await svc.haal_op(session, user.tenant_id, view_id)


@router.patch("/{view_id}", response_model=ImpactViewRead)
async def wijzig_view(
    view_id: uuid.UUID,
    body: ImpactViewUpdate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.IMPACT_VIEW, Actie.WIJZIGEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Naam/selectie/gedeeld wijzigen — alleen de maker (anders 404)."""
    return await svc.werk_bij(session, user.tenant_id, view_id, body)


@router.delete("/{view_id}", status_code=204)
async def verwijder_view(
    view_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.IMPACT_VIEW, Actie.VERWIJDEREN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Een view verwijderen — alleen de maker (anders 404). Junctie cascadeert mee."""
    await svc.verwijder(session, user.tenant_id, view_id)
    return Response(status_code=204)
