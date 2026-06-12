"""HTTP-routes voor ComponentStructuur (ADR-021 Fase B). RBAC via
`vereist_permissie(Entiteit.COMPONENT_STRUCTUUR, …)`. Het beide-richtingen-leesoverzicht
hangt aan de component-router (`/componenten/{id}/structuur`).
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.component_structuur import (
    ComponentStructuurCreate,
    ComponentStructuurRead,
    ComponentStructuurUpdate,
)
from services import component_structuur_service as svc

router = APIRouter(prefix="/component-structuren", tags=["bwb:component-structuur"])


@router.post("", response_model=ComponentStructuurRead, status_code=201)
async def maak_structuur(
    body: ComponentStructuurCreate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.COMPONENT_STRUCTUUR, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.maak_aan(session, user.tenant_id, body)


@router.patch("/{structuur_id}", response_model=ComponentStructuurRead)
async def werk_structuur_bij(
    structuur_id: uuid.UUID,
    body: ComponentStructuurUpdate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.COMPONENT_STRUCTUUR, Actie.WIJZIGEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.werk_bij(session, user.tenant_id, structuur_id, body)


@router.delete("/{structuur_id}", status_code=204)
async def verwijder_structuur(
    structuur_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.COMPONENT_STRUCTUUR, Actie.VERWIJDEREN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    await svc.verwijder(session, user.tenant_id, structuur_id)
    return Response(status_code=204)
