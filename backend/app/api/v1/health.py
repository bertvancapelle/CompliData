"""Health endpoint — liveness + readiness."""
from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_factory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Liveness + readiness check."""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {"status": "ok" if db_status == "ok" else "degraded", "db": db_status}
