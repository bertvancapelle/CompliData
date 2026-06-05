---
name: complidata-security
description: Security-patronen voor CompliData (Zero Trust, httpOnly cookies, NCSC, RLS). Beschrijft de werkelijke V001-staat.
stack: Keycloak 24.x, FastAPI middleware, Redis, PostgreSQL RLS
bijgewerkt: V001
---

# CompliData Security Skill

## Kernregel: httpOnly cookies — geen localStorage

```javascript
// VERBODEN
localStorage.setItem('token', ...)
```

Sessie loopt via de `cd_session` httpOnly cookie (`HttpOnly`, `Secure`,
`SameSite=Strict`). De backend leest de cookie en valideert de Keycloak-JWT
via JWKS.

## SecurityHeadersMiddleware — exact 6 headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## OriginCheckMiddleware

- Controleert de Origin-header op muterende methodes (POST/PUT/PATCH/DELETE).
- Uitzondering: `complidata_test_mode` accepteert requests zonder Origin.
- Bij mismatch/ontbreken: HTTP 403, foutcode `ORIGIN_GEWEIGERD`.

## Auth endpoint-patroon

```python
# /api/v1/auth/me — 401 TOKEN_ONGELDIG zonder geldige sessie
@router.get("/auth/me")
async def me(request: Request, user: AuthenticatedUser = Depends(get_current_user)):
    return asdict(user)

# /api/v1/auth/logout — wist de cookie
@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(settings.cookie_name, domain=settings.cookie_domain,
        samesite=settings.cookie_samesite, secure=settings.cookie_secure, httponly=True)
    return {"status": "uitgelogd"}
```

`get_current_user` zonder cookie → 401; bij decode-fout → 401 + Redis
auth-fail-counter (IP gepseudonimiseerd).

## cd_app vs cd_admin

```python
# CORRECT — cd_app (non-superuser, RLS actief)
DATABASE_URL = "postgresql://cd_app:..."

# VERBODEN — cd_admin omzeilt RLS, nooit in applicatie-schrijfpaden
DATABASE_URL = "postgresql://cd_admin:..."
```

## Dubbele tenant-bescherming

1. **RLS** via `set_config('app.tenant_id', :tid, false)` — databaseniveau.
2. **Expliciete `tenant_id`-filter** in elke query — applicatieniveau (te
   hanteren zodra module-queries worden geschreven).

## NCSC-richtlijnen (niet NIST)

CompliData volgt **NCSC** (Nederlandse overheid) als beveiligingskader.
Gebruik nooit NIST als primaire referentie.

## IP-pseudonimisering

Auth-fail-counters in Redis gebruiken een SHA-256 hash van het IP-adres
(`hash_waarde`) — nooit het ruwe IP opslaan (AVG, privacy by design).

## Stubs en openstaande ADRs (V001)

| Onderdeel | Status |
|---|---|
| RBAC / `_load_roles()` | Stub — geeft `[]` — ADR-010 open |
| Audit trail / hash-chaining | Niet geïmplementeerd — ADR-006 open |
| Login/callback PKCE-flow | Niet geïmplementeerd — ADR-002 open |
| MFA-config Keycloak | Realm aanwezig; MFA-policy nog in te stellen |
