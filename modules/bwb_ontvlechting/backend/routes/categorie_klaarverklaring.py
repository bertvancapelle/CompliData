"""HTTP-routes — categorie-klaarverklaring (ADR-027 slice 1).

Eigen routebestand (`/klaarverklaringen`) — eigen registratie-feit (eigen tabel/service). RBAC via
de nieuwe `KLAARVERKLARING`-entiteit (Viewer L · Medewerker LAW · Beheerder LAWV · Auditor L).
Aanmaken = AANMAKEN; statuswijziging (klaar↔open) = WIJZIGEN. Dunne handlers; logica in de service.
Foutgedrag conform de module-conventie (401/403/404/409-envelope; 422 native of envelope).

Route-volgorde: lijst (`""`) vóór de dynamische `/{klaarverklaring_id}`.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.categorie_klaarverklaring import (
    KlaarverklaringCreate,
    KlaarverklaringRead,
    KlaarverklaringStatusWijzig,
)
from services import categorie_klaarverklaring_service as svc

router = APIRouter(prefix="/klaarverklaringen", tags=["bwb:klaarverklaring"])


@router.get("", response_model=list[KlaarverklaringRead])
async def lijst_klaarverklaringen(
    component_id: uuid.UUID | None = Query(None),
    categorie_nr: int | None = Query(None),
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KLAARVERKLARING, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Klaarverklaringen binnen de tenant; optioneel gefilterd op component en/of categorie_nr."""
    return await svc.lijst(session, user.tenant_id, component_id=component_id, categorie_nr=categorie_nr)


@router.post("", response_model=KlaarverklaringRead, status_code=201)
async def maak_klaarverklaring(
    body: KlaarverklaringCreate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KLAARVERKLARING, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.maak_aan(session, user.tenant_id, body)


@router.get("/{klaarverklaring_id}", response_model=KlaarverklaringRead)
async def haal_klaarverklaring(
    klaarverklaring_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KLAARVERKLARING, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.haal_op(session, user.tenant_id, klaarverklaring_id)


@router.patch("/{klaarverklaring_id}", response_model=KlaarverklaringRead)
async def wijzig_klaarverklaring_status(
    klaarverklaring_id: uuid.UUID,
    body: KlaarverklaringStatusWijzig,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KLAARVERKLARING, Actie.WIJZIGEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.wijzig_status(session, user.tenant_id, klaarverklaring_id, body)
