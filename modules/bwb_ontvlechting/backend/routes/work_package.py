"""HTTP-routes — Work Package (ADR-023 Fase E, E2).

Dunne handlers; RBAC via `vereist_permissie(Entiteit.WORK_PACKAGE, …)`. CRUD + het zetten
van een bovenliggend pakket (met server-side cycluspreventie) + een subboom-lees-traversal.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, Response

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.work_package import (
    WorkPackageBoomItem,
    WorkPackageCreate,
    WorkPackagePagina,
    WorkPackageRead,
    WorkPackageUpdate,
)
from services import work_package_service as svc

router = APIRouter(prefix="/work-packages", tags=["bwb:work_package"])


def _fout(http_status: int, code: str, bericht: str) -> JSONResponse:
    return JSONResponse(
        status_code=http_status,
        content={"fout": {"code": code, "http_status": http_status, "bericht": bericht}},
    )


@router.get("", response_model=WorkPackagePagina)
async def lijst_work_packages(
    limit: int = Query(25, ge=1, le=100),
    after: str | None = Query(None),
    zoek: str | None = Query(None, max_length=255),
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.WORK_PACKAGE, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    try:
        items, volgende = await svc.lijst(session, user.tenant_id, limit=limit, after=after, zoek=zoek)
    except ValueError:
        return _fout(400, "ONGELDIGE_CURSOR", "De opgegeven paginacursor is ongeldig.")
    return {"items": items, "volgende_cursor": volgende}


@router.post("", response_model=WorkPackageRead, status_code=201)
async def maak_work_package(
    body: WorkPackageCreate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.WORK_PACKAGE, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.maak_aan(session, user.tenant_id, body)


@router.get("/{work_package_id}", response_model=WorkPackageRead)
async def haal_work_package(
    work_package_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.WORK_PACKAGE, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.lees_detail(session, user.tenant_id, work_package_id)


@router.get("/{work_package_id}/subboom", response_model=list[WorkPackageBoomItem])
async def subboom(
    work_package_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.WORK_PACKAGE, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Read-only subboom (afstammelingen met niveau + pad)."""
    return await svc.subboom(session, user.tenant_id, work_package_id)


@router.patch("/{work_package_id}", response_model=WorkPackageRead)
async def werk_work_package_bij(
    work_package_id: uuid.UUID,
    body: WorkPackageUpdate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.WORK_PACKAGE, Actie.WIJZIGEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.werk_bij(session, user.tenant_id, work_package_id, body)


@router.delete("/{work_package_id}", status_code=204)
async def verwijder_work_package(
    work_package_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.WORK_PACKAGE, Actie.VERWIJDEREN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    await svc.verwijder(session, user.tenant_id, work_package_id)
    return Response(status_code=204)
