"""HTTP-route voor ChecklistVraag — scoring-read (de actieve, tenant-eigen vragenset).

ADR-022 W1: `checklistvraag` is tenant-scoped (RLS); deze read levert de **actieve**
vragen. ADR-022 Fase E: optioneel gescoped op `componenttype` van het te scoren
component (symmetrisch met de engine-telling). Eén respons, geen cursor (kleine set).
"""
from fastapi import APIRouter, Depends, Query
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
    componenttype: str | None = Query(None, max_length=60),
    _user: AuthenticatedUser = Depends(vereist_permissie(Entiteit.CHECKLISTSCORE, Actie.LEZEN)),
    session: AsyncSession = Depends(get_tenant_session),
):
    """De actieve tenant-vragenset (scoring-read), optioneel gescoped op `componenttype`."""
    return await svc.lijst_alle(session, componenttype)
