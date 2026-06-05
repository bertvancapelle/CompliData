"""Autorisatie-guard (ADR-010).

`vereist_permissie(entiteit, actie)` levert een FastAPI-dependency die eerst de
sessie valideert (`get_current_user` → 401 zonder geldige sessie) en daarna de
rechtenmatrix raadpleegt. Onvoldoende rechten ⇒ `OnvoldoendeRechten`, door de
handler omgezet naar HTTP 403 in het canonieke foutformaat.

Autorisatie is uitsluitend server-side; de client wordt nooit vertrouwd.
RBAC staat náást de tenant-isolatie (RLS), niet in plaats daarvan.
"""
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.rbac import Actie, Entiteit, heeft_permissie
from app.middleware.auth import AuthenticatedUser, get_current_user


class OnvoldoendeRechten(Exception):
    """Geldige sessie, maar de rol(len) dekken de gevraagde actie niet."""

    def __init__(self, entiteit: Entiteit, actie: Actie):
        self.entiteit = entiteit
        self.actie = actie


def vereist_permissie(entiteit: Entiteit, actie: Actie):
    """Bouw een dependency die `entiteit`/`actie` afdwingt tegen de matrix."""

    async def _guard(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not heeft_permissie(user.roles, entiteit, actie):
            raise OnvoldoendeRechten(entiteit, actie)
        return user

    return _guard


async def onvoldoende_rechten_handler(
    request: Request, exc: OnvoldoendeRechten
) -> JSONResponse:
    """HTTP 403 — canoniek foutformaat, geen architectuurdetails."""
    return JSONResponse(
        status_code=403,
        content={
            "fout": {
                "code": "ONVOLDOENDE_RECHTEN",
                "http_status": 403,
                "bericht": "Onvoldoende rechten voor deze actie.",
            }
        },
    )
