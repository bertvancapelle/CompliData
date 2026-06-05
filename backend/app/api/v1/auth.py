"""Auth endpoints — sessie-introspectie + logout.

V001-basis: `/auth/me` levert de geauthenticeerde gebruiker uit de
httpOnly sessie-cookie. De volledige login/callback PKCE-flow en RBAC
(ADR-002, ADR-010) worden tijdens module-ontwikkeling uitgebouwd.
"""
from dataclasses import asdict

from fastapi import APIRouter, Depends, Request, Response

from app.core.config import settings
from app.middleware.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def me(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Geef de huidige geauthenticeerde gebruiker terug (401 zonder geldige sessie)."""
    return asdict(user)


@router.post("/logout")
async def logout(response: Response):
    """Wis de sessie-cookie. SSO-logout via Keycloak volgt met de auth-flow."""
    response.delete_cookie(
        key=settings.cookie_name,
        domain=settings.cookie_domain,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
        httponly=True,
    )
    return {"status": "uitgelogd"}
