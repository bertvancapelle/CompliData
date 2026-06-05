"""Auth endpoints — login/callback (PKCE), sessie-introspectie + logout.

`/auth/login` start de OAuth2 Authorization Code-flow met PKCE (ADR-002):
`code_verifier`/`state`/`nonce` worden server-side in Redis bewaard (gekoppeld
via `state`, nooit client-leesbaar) en de gebruiker wordt naar Keycloak
geredirect. `/auth/callback` wisselt de code server-side in, valideert het
id_token (nonce/iss/aud/exp) en zet de `cd_session` httpOnly cookie die door
`/auth/me` wordt gevalideerd.
"""
import json
import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, Request, Response
from pydantic import ValidationError
from starlette.responses import JSONResponse, RedirectResponse
from urllib.parse import urlencode

from app.core.config import settings
from app.core.keycloak import (
    AUTHORIZATION_URL,
    decode_id_token,
    exchange_code_for_tokens,
)
from app.core.pkce import (
    code_challenge_s256,
    generate_code_verifier,
    generate_nonce,
    generate_state,
)
from app.core.redis import get_redis
from app.middleware.auth import (
    AuthenticatedUser,
    _increment_fail_counter,
    get_current_user,
)
from app.schemas.auth import CallbackParams, LoginParams
from app.utils.crypto import hash_waarde

router = APIRouter(prefix="/auth", tags=["auth"])

_log = logging.getLogger("cd.auth")

_STATE_PREFIX = "auth_login:"


def _effective_redirect_uri() -> str:
    """OAuth2 redirect_uri — configureerbaar, anders afgeleid van platform_origin."""
    return settings.oidc_redirect_uri or f"{settings.platform_origin}/api/v1/auth/callback"


def _valideer_next(bestemming: str | None) -> str:
    """Open-redirect-bescherming: sta alleen een same-origin relatief pad toe."""
    if not bestemming:
        return "/"
    if (
        bestemming.startswith("/")
        and not bestemming.startswith("//")
        and "\\" not in bestemming
        and "://" not in bestemming
    ):
        return bestemming
    return "/"


def _fout(http_status: int, code: str, bericht: str) -> JSONResponse:
    """Canoniek foutformaat — geen stacktraces of architectuurdetails."""
    return JSONResponse(
        status_code=http_status,
        content={"fout": {"code": code, "http_status": http_status, "bericht": bericht}},
    )


@router.get("/login")
async def login(request: Request):
    """Start de Authorization Code + PKCE-flow; redirect naar Keycloak."""
    try:
        params = LoginParams(**dict(request.query_params))
    except ValidationError:
        return _fout(400, "LOGIN_PARAMS_ONGELDIG", "Ongeldige login-parameters.")

    veilige_next = _valideer_next(params.next)
    verifier = generate_code_verifier()
    challenge = code_challenge_s256(verifier)
    state = generate_state()
    nonce = generate_nonce()

    r = await get_redis()
    await r.set(
        f"{_STATE_PREFIX}{state}",
        json.dumps({"verifier": verifier, "nonce": nonce, "next": veilige_next}),
        ex=settings.auth_state_ttl,
    )

    query = urlencode(
        {
            "client_id": settings.keycloak_client_id,
            "redirect_uri": _effective_redirect_uri(),
            "response_type": "code",
            "scope": "openid",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": state,
            "nonce": nonce,
        }
    )
    return RedirectResponse(url=f"{AUTHORIZATION_URL}?{query}", status_code=302)


@router.get("/callback")
async def callback(request: Request):
    """Verwerk de Keycloak-redirect: valideer state, wissel code in, zet sessie."""
    ip_hash = hash_waarde(request.client.host if request.client else None) or "unknown"

    try:
        params = CallbackParams(**dict(request.query_params))
    except ValidationError:
        return _fout(400, "CALLBACK_PARAMS_ONGELDIG", "Ongeldige callback-parameters.")

    if params.error:
        return _fout(400, "AUTH_GEWEIGERD", "Authenticatie is geweigerd.")
    if not params.code or not params.state:
        return _fout(400, "CALLBACK_PARAMS_ONGELDIG", "Ontbrekende code of state.")

    # State eenmalig consumeren (CSRF + replay-bescherming).
    r = await get_redis()
    ruw = await r.getdel(f"{_STATE_PREFIX}{params.state}")
    if not ruw:
        await _increment_fail_counter(ip_hash)
        return _fout(400, "STATE_ONGELDIG", "Sessie-aanvraag verlopen of ongeldig.")
    opslag = json.loads(ruw)

    redirect_uri = _effective_redirect_uri()
    try:
        tokens = await exchange_code_for_tokens(params.code, redirect_uri, opslag["verifier"])
    except Exception:
        await _increment_fail_counter(ip_hash)
        _log.warning("AUTH_FAIL: token-uitwisseling mislukt (ip_hash=%s)", ip_hash)
        return _fout(502, "TOKEN_UITWISSELING_MISLUKT", "Inloggen mislukt.")

    id_token = tokens.get("id_token")
    access_token = tokens.get("access_token")
    if not id_token or not access_token:
        await _increment_fail_counter(ip_hash)
        return _fout(502, "TOKEN_UITWISSELING_MISLUKT", "Inloggen mislukt.")

    try:
        decode_id_token(id_token, opslag["nonce"])
    except Exception:
        await _increment_fail_counter(ip_hash)
        _log.warning("AUTH_FAIL: id_token-validatie mislukt (ip_hash=%s)", ip_hash)
        return _fout(401, "ID_TOKEN_ONGELDIG", "Inloggen mislukt.")

    bestemming = _valideer_next(opslag.get("next"))
    response = RedirectResponse(url=bestemming, status_code=303)
    response.set_cookie(
        key=settings.cookie_name,
        value=access_token,
        max_age=settings.access_token_max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )
    return response


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
