"""Authentication middleware.

Extraheert JWT uit httpOnly cookie en verifieert via Keycloak JWKS.

Faalgedrag:
- 401: token ontbreekt of ongeldig
- 403: tenant ontbreekt in token

RBAC (rollen) is NOG NIET geïmplementeerd in V001 — zie ADR-010
(RBAC en rollenstructuur Keycloak). `_load_roles` is een bewuste stub
die een lege lijst teruggeeft tot ADR-010 de definitieve rolbron vaststelt.
"""
import asyncio
import logging
from dataclasses import dataclass, field

from fastapi import Request, HTTPException

from app.core.config import settings
from app.core.keycloak import decode_token
from app.utils.crypto import hash_waarde

_auth_log = logging.getLogger("cd.auth")
AUTH_FAIL_TTL = 900  # 15 min


async def _increment_fail_counter(ip_hash: str) -> None:
    """Verhoog auth-fail counter in Redis. Fire-and-forget."""
    try:
        from app.core.redis import get_redis

        r = await get_redis()
        key = f"auth_fail:{ip_hash}"
        await r.incr(key)
        await r.expire(key, AUTH_FAIL_TTL)
    except Exception:
        _auth_log.warning("Redis auth_fail counter mislukt voor %s", ip_hash)


@dataclass(frozen=True)
class AuthenticatedUser:
    sub: str
    tenant_id: str
    roles: list[str] = field(default_factory=list)
    email: str | None = None


async def _load_roles(keycloak_sub: str, tenant_id: str) -> list[str]:
    """STUB — RBAC nog niet ontworpen (ADR-010).

    In V001 worden geen rollen geladen. Vul deze functie wanneer ADR-010
    de rolbron vaststelt (DB-tabel of Keycloak-claim).
    """
    return []


async def get_current_user(request: Request) -> AuthenticatedUser:
    """Dependency: extract and verify user from httpOnly session cookie."""
    token = request.cookies.get(settings.cookie_name)
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"code": "TOKEN_ONGELDIG", "bericht": "Geen sessie gevonden."},
        )

    try:
        payload = decode_token(token)
    except Exception:
        ip_h = hash_waarde(request.client.host if request.client else None)
        try:
            asyncio.get_running_loop().create_task(
                _increment_fail_counter(ip_h or "unknown")
            )
        except RuntimeError:
            _auth_log.warning("AUTH_FAIL: token validatie mislukt")
        raise HTTPException(
            status_code=401,
            detail={"code": "TOKEN_ONGELDIG", "bericht": "Sessie ongeldig."},
        )

    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "TENANT_MISMATCH",
                "bericht": "Tenant niet gevonden in token.",
            },
        )

    roles = await _load_roles(payload["sub"], tenant_id)

    return AuthenticatedUser(
        sub=payload["sub"],
        tenant_id=tenant_id,
        roles=roles,
        email=payload.get("email"),
    )
