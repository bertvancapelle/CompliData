"""Service-laag voor ChecklistVraag — platform-brede referentiedata (read-only).

`checklistvraag` is BEWUST niet tenant-scoped: het heeft geen RLS en geen
`tenant_id` (89 vaste vragen, gedeeld over alle tenants). Daarom géén
`tenant_id`-filter en géén `set_config`-afhankelijkheid; alle tenants zien
dezelfde set. (Wijk hier niet van af door "scoping toe te voegen".)
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import ChecklistVraag


async def lijst_alle(session: AsyncSession) -> list[ChecklistVraag]:
    """Alle ChecklistVragen, gesorteerd op `code`. Geen tenant-filter (referentiedata)."""
    stmt = select(ChecklistVraag).order_by(ChecklistVraag.code)
    return list((await session.execute(stmt)).scalars().all())
