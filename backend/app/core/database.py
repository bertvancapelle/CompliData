import uuid
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Platform-engine op cd_platform (ADR-012) — voor platform-endpoints. Non-superuser,
# géén RLS-/tenant-context, géén toegang tot tenant-tabellen. cd_admin komt NIET
# meer in de app-laag voor (OP-11).
platform_engine = create_async_engine(settings.platform_database_url, echo=False)
platform_session_factory = async_sessionmaker(
    platform_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session(tenant_id: str):
    """Yield a database session with RLS tenant context set."""
    async with async_session_factory() as session:
        await session.execute(text("SELECT set_config('app.tenant_id', :tid, false)"), {"tid": tenant_id})
        yield session


@asynccontextmanager
async def get_worker_session(tenant_id: uuid.UUID):
    """AsyncSession met RLS-context voor achtergrond-workers.

    Verse sessie per event — voorkomt RLS-context lek tussen tenants.
    """
    async with async_session_factory() as session:
        await session.execute(
            text("SELECT set_config('app.tenant_id', :tid, false)"),
            {"tid": str(tenant_id)},
        )
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_platform_db_session():
    """AsyncSession zonder RLS-context — alleen voor platform-brede queries."""
    async with async_session_factory() as session:
        yield session
