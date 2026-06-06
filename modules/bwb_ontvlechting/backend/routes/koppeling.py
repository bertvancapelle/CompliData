"""HTTP-routes voor de entiteit Koppeling (P5-vervolg, ADR-009/010).

Dunne handlers; zelfde patroon als de andere kind-entiteiten. Optionele
tenant-scoped lijst-filters `?bron_applicatie_id=` / `?doel_applicatie_id=`.

Foutgedrag: 401 · 403 `ONVOLDOENDE_RECHTEN` · 404 `NIET_GEVONDEN` (record óf
bron/doel-ouder buiten tenant) · 409 `KOPPELING_CONFLICT` (DB-CHECK-backstop) ·
422 (`bron == doel` of Pydantic) · 400 `ONGELDIGE_CURSOR`.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, Response

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.koppeling import (
    KoppelingCreate,
    KoppelingPagina,
    KoppelingRead,
    KoppelingUpdate,
)
from services import koppeling_service as svc

router = APIRouter(prefix="/koppelingen", tags=["bwb:koppeling"])


def _fout(http_status: int, code: str, bericht: str) -> JSONResponse:
    """Canoniek foutformaat — geen stacktraces of architectuurdetails."""
    return JSONResponse(
        status_code=http_status,
        content={"fout": {"code": code, "http_status": http_status, "bericht": bericht}},
    )


@router.get("", response_model=KoppelingPagina)
async def lijst_koppelingen(
    limit: int = Query(25, ge=1, le=100),
    after: str | None = Query(None),
    bron_applicatie_id: uuid.UUID | None = Query(None),
    doel_applicatie_id: uuid.UUID | None = Query(None),
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KOPPELING, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    try:
        items, volgende = await svc.lijst(
            session,
            user.tenant_id,
            limit=limit,
            after=after,
            bron_applicatie_id=bron_applicatie_id,
            doel_applicatie_id=doel_applicatie_id,
        )
    except ValueError:
        return _fout(400, "ONGELDIGE_CURSOR", "De opgegeven paginacursor is ongeldig.")
    return {"items": items, "volgende_cursor": volgende}


@router.get("/{koppeling_id}", response_model=KoppelingRead)
async def haal_koppeling(
    koppeling_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KOPPELING, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.haal_op(session, user.tenant_id, koppeling_id)


@router.post("", response_model=KoppelingRead, status_code=201)
async def maak_koppeling(
    body: KoppelingCreate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KOPPELING, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Maak een koppeling; bron- én doel-applicatie moeten binnen de tenant bestaan."""
    return await svc.maak_aan(session, user.tenant_id, body)


@router.patch("/{koppeling_id}", response_model=KoppelingRead)
async def werk_koppeling_bij(
    koppeling_id: uuid.UUID,
    body: KoppelingUpdate,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KOPPELING, Actie.WIJZIGEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    return await svc.werk_bij(session, user.tenant_id, koppeling_id, body)


@router.delete("/{koppeling_id}", status_code=204)
async def verwijder_koppeling(
    koppeling_id: uuid.UUID,
    user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.KOPPELING, Actie.VERWIJDEREN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    await svc.verwijder(session, user.tenant_id, koppeling_id)
    return Response(status_code=204)
