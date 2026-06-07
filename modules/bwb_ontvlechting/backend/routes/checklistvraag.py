"""HTTP-route voor ChecklistVraag — read-only, platform-brede referentiedata.

BEWUST géén tenant-scoping: `checklistvraag` heeft geen RLS/`tenant_id` en wordt
door alle tenants gedeeld (de 89 vaste vragen). De `vereist_permissie(CHECKLISTSCORE,
LEZEN)`-guard regelt de toegang; de query filtert niet op tenant. Eén respons,
geen cursor (kleine vaste set).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Actie, Entiteit
from app.middleware.auth import AuthenticatedUser
from app.middleware.authz import vereist_permissie
from app.middleware.tenant import get_tenant_session
from schemas.checklistvraag import ChecklistVraagRead
from services import checklistvraag_service as svc

router = APIRouter(prefix="/checklistvragen", tags=["bwb:checklistvraag"])


@router.get("", response_model=list[ChecklistVraagRead])
async def lijst_checklistvragen(
    _user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.CHECKLISTSCORE, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """Alle ChecklistVragen (referentiedata), gesorteerd op `code`."""
    return await svc.lijst_alle(session)
