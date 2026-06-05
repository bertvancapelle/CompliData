import logging

import httpx
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger("cd.keycloak")

OIDC_BASE = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect"
OIDC_EXTERNAL_BASE = f"{settings.keycloak_external_url or settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect"
JWKS_URL = f"{OIDC_BASE}/certs"
TOKEN_URL = f"{OIDC_BASE}/token"
USERINFO_URL = f"{OIDC_BASE}/userinfo"
ADMIN_BASE = f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}"


@lru_cache(maxsize=1)
def get_jwks_client():
    """Lazy import — jwt is only needed at runtime."""
    import jwt

    return jwt.PyJWKClient(JWKS_URL, cache_keys=True)


def decode_token(token: str) -> dict:
    """Decode and verify a Keycloak JWT access token."""
    import jwt

    jwks_client = get_jwks_client()
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.keycloak_client_id,
        issuer=f"{settings.keycloak_external_url or settings.keycloak_url}/realms/{settings.keycloak_realm}",
    )


async def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.keycloak_client_id,
                "client_secret": settings.keycloak_client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_end_session_url(id_token_hint: str) -> str:
    """Bouw de Keycloak end-session URL voor volledige SSO-logout."""
    return (
        f"{OIDC_EXTERNAL_BASE}/logout"
        f"?id_token_hint={id_token_hint}"
        f"&post_logout_redirect_uri={settings.platform_origin}/login"
    )


async def get_admin_token() -> str:
    """Verkrijg een Keycloak Admin API token via master realm."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.keycloak_url}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": settings.keycloak_admin_user,
                "password": settings.keycloak_admin_password,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def refresh_access_token(refresh_token: str) -> dict:
    """Use refresh token to obtain a new access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.keycloak_client_id,
                "client_secret": settings.keycloak_client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()
