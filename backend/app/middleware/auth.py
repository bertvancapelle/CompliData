"""Authentication middleware.

Extraheert JWT uit httpOnly cookie en verifieert via Keycloak JWKS.

Faalgedrag:
- 401: token ontbreekt of ongeldig
- 403: tenant ontbreekt in token

RBAC (ADR-010): `_load_roles` mapt de Keycloak-rolclaims (realm- en
client-rollen) op de platform-rollen Viewer/Medewerker/Beheerder/Auditor via
`app.core.rbac`. Onbekende/ontbrekende rollen ⇒ lege lijst (fail-secure).
Autorisatie wordt afgedwongen met `vereist_permissie(...)` (middleware/authz).
"""
import asyncio
import logging
from dataclasses import dataclass, field

from fastapi import Request, HTTPException
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.keycloak import decode_token
from app.utils.crypto import hash_waarde

_auth_log = logging.getLogger("cd.auth")
AUTH_FAIL_TTL = 900  # 15 min


class NietGeauthenticeerd(HTTPException):
    """401 — geen geldige sessie (ADR-014 / OP-7).

    De echte app levert het canonieke `{"fout":{...}}`-envelope via de
    geregistreerde `niet_geauthenticeerd_handler` (main.py). Subclass van
    HTTPException, zodat een app zónder die handler (bv. een minimale test-app)
    nog steeds gewoon HTTP 401 teruggeeft i.p.v. 500.
    """

    def __init__(self, bericht: str = "Niet geauthenticeerd."):
        self.bericht = bericht
        super().__init__(status_code=401, detail=bericht)


async def niet_geauthenticeerd_handler(request: Request, exc: NietGeauthenticeerd) -> JSONResponse:
    """HTTP 401 — canoniek foutformaat (ADR-014 B1). Code: NIET_GEAUTHENTICEERD."""
    return JSONResponse(
        status_code=401,
        content={
            "fout": {
                "code": "NIET_GEAUTHENTICEERD",
                "http_status": 401,
                "bericht": getattr(exc, "bericht", "Niet geauthenticeerd."),
            }
        },
    )


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


async def _load_roles(payload: dict) -> list[str]:
    """Laad de platform-rollen uit de Keycloak-JWT-claims (ADR-010).

    Mapt realm- én client-rollen op Viewer/Medewerker/Beheerder/Auditor;
    onbekende rollen worden genegeerd (fail-secure → geen rechten).
    """
    from app.core.rbac import extract_rollen

    return extract_rollen(payload)


async def get_current_user(request: Request) -> AuthenticatedUser:
    """Dependency: extract and verify user from httpOnly session cookie."""
    token = request.cookies.get(settings.cookie_name)
    if not token:
        raise NietGeauthenticeerd("Geen sessie gevonden.")

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
        raise NietGeauthenticeerd("Sessie ongeldig.")

    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "TENANT_MISMATCH",
                "bericht": "Tenant niet gevonden in token.",
            },
        )

    roles = await _load_roles(payload)

    return AuthenticatedUser(
        sub=payload["sub"],
        tenant_id=tenant_id,
        roles=roles,
        email=payload.get("email"),
    )


@dataclass(frozen=True)
class PlatformUser:
    """Platform-account (ADR-012) — bóven tenants, GEEN tenant_id."""

    sub: str
    roles: list[str] = field(default_factory=list)
    email: str | None = None


async def get_current_platform_user(request: Request) -> "PlatformUser":
    """Dependency voor PLATFORM-endpoints: valideer sessie, lees platform-rollen.

    Vereist BEWUST geen `tenant_id` (platform-accounts hebben er geen). Levert
    uitsluitend platform-rollen; tenant-rollen blijven buiten dit domein. Een
    tenant-account krijgt hier een lege rollenlijst ⇒ de platform-guard weigert.
    """
    token = request.cookies.get(settings.cookie_name)
    if not token:
        raise NietGeauthenticeerd("Geen sessie gevonden.")

    try:
        payload = decode_token(token)
    except Exception:
        ip_h = hash_waarde(request.client.host if request.client else None)
        try:
            asyncio.get_running_loop().create_task(
                _increment_fail_counter(ip_h or "unknown")
            )
        except RuntimeError:
            _auth_log.warning("AUTH_FAIL: token validatie mislukt (platform)")
        raise NietGeauthenticeerd("Sessie ongeldig.")

    from app.core.platform_rbac import extract_platform_rollen

    return PlatformUser(
        sub=payload["sub"],
        roles=extract_platform_rollen(payload),
        email=payload.get("email"),
    )
