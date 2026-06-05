"""Tenant context middleware.

Zet de PostgreSQL session-variabele `app.tenant_id` zodat Row Level
Security alle queries filtert op de geauthenticeerde tenant.
"""
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
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
    """Read-only sessie zonder RLS-context — alleen voor platform-brede reads.

    Gebruikt de cd_app verbinding (geen admin nodig voor reads).
    """
    async with async_session_factory() as session:
        yield session


async def get_admin_session():
    """Admin database sessie zonder RLS-filter — gebruikt cd_admin verbinding die RLS bypasses.

    Uitsluitend voor platform-beheer; nooit voor tenant-scoped writes.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from app.core.config import settings
    engine = create_async_engine(settings.admin_database_url, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
