"""Tenant context middleware.

Zet de PostgreSQL session-variabele `app.tenant_id` zodat Row Level
Security alle queries filtert op de geauthenticeerde tenant.
"""
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, platform_session_factory
from app.middleware.auth import AuthenticatedUser, get_current_user


async def get_tenant_session(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AsyncSession:
    """Yield a DB session scoped to the authenticated user's tenant."""
    async with async_session_factory() as session:
        await session.execute(
            text("SELECT set_config('app.tenant_id', :tid, false)"), {"tid": user.tenant_id}
        )
        try:
            yield session
        finally:
            await session.close()


async def get_platform_session():
    """Platform-sessie op cd_platform (ADR-012) — voor platform-endpoints
    (tenant-provisioning, platforminstellingen).

    cd_platform is non-superuser, heeft GEEN RLS-/tenant-context en GEEN toegang
    tot tenant-tabellen; cd_admin komt hier NIET aan te pas (OP-11). Geen
    tenant-scoped werk — dat loopt via `get_tenant_session` onder RLS.
    """
    async with platform_session_factory() as session:
        yield session
