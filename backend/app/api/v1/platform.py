"""Platform-endpoints (ADR-012) — tenant-provisioning.

Geautoriseerd via `vereist_platform_permissie` (alleen platform-rollen) en
uitgevoerd op `get_platform_session` (lk_platform, non-superuser, geen
tenant-/RLS-context). Een tenant aanmaken raakt geen tenant-gescopete data —
de nieuwe tenant start leeg; RLS-isolatie blijft intact.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.platform_rbac import PlatformEntiteit
from app.core.rbac import Actie
from app.middleware.authz import vereist_platform_permissie
from app.middleware.tenant import get_platform_session
from app.models.platform import Tenant
from app.schemas.platform import TenantAanmaken, TenantResponse

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/tenants", response_model=list[TenantResponse])
async def lijst_tenants(
    _platform_user=Depends(vereist_platform_permissie(PlatformEntiteit.TENANT, Actie.LEZEN)),
    session: AsyncSession = Depends(get_platform_session),
):
    """Lijst van tenants (platform-metadata). Lezen: platformbeheerder + operator."""
    result = await session.execute(select(Tenant).order_by(Tenant.created_at))
    return result.scalars().all()


@router.post("/tenants", response_model=TenantResponse, status_code=201)
async def maak_tenant(
    body: TenantAanmaken,
    _platform_user=Depends(vereist_platform_permissie(PlatformEntiteit.TENANT, Actie.AANMAKEN)),
    session: AsyncSession = Depends(get_platform_session),
):
    """Maak/onboard een tenant. Aanmaken: uitsluitend platformbeheerder."""
    bestaat = await session.execute(
        select(Tenant).where(or_(Tenant.naam == body.naam, Tenant.slug == body.slug))
    )
    if bestaat.scalars().first() is not None:
        return JSONResponse(
            status_code=409,
            content={
                "fout": {
                    "code": "TENANT_BESTAAT_AL",
                    "http_status": 409,
                    "bericht": "Een tenant met deze naam of slug bestaat al.",
                }
            },
        )

    tenant = Tenant(naam=body.naam, slug=body.slug)
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return tenant
