# ADR-015 — Refresh-token-subsysteem: Keycloak-gedelegeerd, Redis-opslag

| | |
|---|---|
| **Status** | Aanvaard |
| **Datum** | 2026-06-07 |
| **Beslissers** | Bert van Capelle (G. van Capelle Beheer B.V.) |
| **Gerelateerd** | OP-3 · ADR-002 (PKCE login/callback) · ADR-014 (foutformaat) · OP-4 (logout, raakvlak) |

## Context

De `cd_session` httpOnly-cookie (`HttpOnly`/`Secure`/`SameSite=Strict`) bevat het
Keycloak **access-token**, max-age = 15 min; de backend valideert het via JWKS.
Na 15 min verloopt de sessie en moet de gebruiker opnieuw inloggen — er is geen
verlengmechanisme.

Bij de server-side code-exchange in `/auth/callback` (ADR-002) geeft Keycloak
**ook een `refresh_token`** terug, dat nu wordt **weggegooid**. OP-3 vraagt om een
refresh-subsysteem (`/auth/refresh`, server-side opslag, rotatie) zodat de sessie
stil verlengt zonder herauthenticatie.

## Besluit

### B1 — Keycloak-gedelegeerd, geen eigen token-schema
`/auth/refresh` doet `grant_type=refresh_token` tegen het Keycloak
token-endpoint, **volledig server-side** (`client_secret` nooit naar de client).
De app geeft **geen** eigen JWT's uit en bouwt **geen** parallel refresh-schema.
Access-tokenvalidatie blijft via JWKS (ongewijzigd).

### B2 — Opslag in Redis
Het Keycloak-`refresh_token` wordt **server-side in Redis** bewaard, gekoppeld aan
een sessie-identifier. Het staat **nooit** in een browser-zichtbare plek en
**nooit** in de access-cookie. TTL afgestemd op de Keycloak SSO-sessieduur.
**Ephemeer geaccepteerd**: Redis-verlies ⇒ opnieuw inloggen.

### B3 — Rotatie + hergebruik-detectie bij Keycloak
Keycloak's `revoke-refresh-token` (rotatie) is leidend: elke refresh levert een
**nieuw** `refresh_token` dat het oude vervangt — de app bewaart steeds het
nieuwste in Redis. Hergebruik van een ingetrokken token ⇒ Keycloak weigert ⇒ de
app behandelt dit als sessie-einde. De app implementeert **geen** eigen
family-revocatie.

> **Implementatienoot (V008)**: B3 (rotatie/hergebruik-detectie bij Keycloak)
> veronderstelt een **actieve** `revoke-refresh-token`-realmsetting. In de huidige
> realm staat die UIT → de app bewaart wél steeds het nieuwste token, maar oude
> refresh-tokens blijven geldig tot SSO-einde (idle/max = 8u); **echte
> hergebruik-detectie is nog niet actief**. Zie opvolgpunt OP-3-realm-hardening
> (koppelen aan OP-14, realm-hardening).

### B4 — Additief cookie-ontwerp, geen sessiemodel-herontwerp
Het access-token blijft in `cd_session` (15 min). Een server-side
sessie-identifier koppelt aan het Redis-bewaarde refresh-token. Implementatie
(V008): een aparte httpOnly `cd_refresh`-cookie met een opake sessie-id
(`HttpOnly`/`Secure`/`SameSite=Strict`); de id mapt in Redis
(`auth_refresh:{sessie_id}`) naar het refresh-token, nooit client-leesbaar.

### B5 — Contract `/auth/refresh`
`POST /auth/refresh`: lees de sessie-identifier (cookie) → haal het
`refresh_token` uit Redis → wissel bij Keycloak → zet een **nieuw** `cd_session`
en bewaar het **geroteerde** refresh-token in Redis.
- Succes ⇒ 200/204 + nieuwe cookie(s).
- Afwezig/verlopen/ingetrokken ⇒ **401 canoniek**
  `{"fout":{"code":"NIET_GEAUTHENTICEERD","http_status":401,…}}` (ADR-014); het
  onbruikbaar geworden Redis-handle wordt opgeruimd.

### B6 — Frontend: single-flight refresh-on-401
Bij een 401 op een API-call doet de client **één** `/auth/refresh`-poging; bij
succes wordt de oorspronkelijke request herprobeerd, bij mislukken volgt de
bestaande sessie-verloop-flow (login-redirect). Gelijktijdige 401's **delen één**
refresh-poging (geen stampede, geen loop). Herkenning keyt op **HTTP-status**
(consistent met ADR-014 / CD005).

## Gevolgen

**Positief**
- Sessies verlengen stil zonder herlogin; rotatie en hergebruik-detectie liggen
  bij de IdP waar ze horen.
- Minimale blast radius: **geen migratie, geen datamodelwijziging**; sluit aan op
  het bestaande Redis-auth-state-gebruik en de httpOnly-cookie-regel.

**Negatief / aandachtspunten**
- Redis is ephemeer ⇒ Redis-verlies = herlogin (geaccepteerd, B2).
- **Keycloak-clientconfig is een voorwaarde**: refresh enabled,
  `revoke-refresh-token` aan, SSO session idle/max passend. (Bevestigd dat de
  code-exchange een `refresh_token` teruggeeft; `revoke-refresh-token` staat nog
  UIT — zie B3-implementatienoot.)
- **CSRF**: `/auth/refresh` is een state-changing POST met cookie ⇒ `SameSite=Strict`
  + de bestaande `OriginCheckMiddleware` beschermen.
- **Raakvlak OP-4**: logout moet óók het Redis-refresh-token + de Keycloak-sessie
  intrekken — daar afhechten.

## Alternatieven overwogen

- **Eigen/app-issued refresh-tokens of JWT-uitgifte** — afgewezen (B1): dubbel
  token-beheer en eigen revocatie-complexiteit terwijl de IdP dit al levert.
- **Postgres refresh-tabel** — afgewezen (B2): persistente opslag is niet nodig;
  Redis (ephemeer) volstaat en sluit aan op het bestaande auth-state-patroon.
- **Herontwerp van het sessiemodel** — afgewezen (B4): additief cookie-ontwerp
  houdt de blast radius klein.

## Niet in scope

- Eigen/app-issued refresh-tokens of JWT-uitgifte (afgewezen, B1).
- Postgres refresh-tabel (afgewezen, B2).
- Herontwerp van het sessiemodel (B4).
- RP-initiated logout (OP-4) — eigen opdracht; wel raakvlak (B6/aandachtspunt).
- Keycloak-realmconfig zelf (infra/config) — wel als voorwaarde benoemd
  (`revoke-refresh-token`, zie B3-implementatienoot / OP-3-realm-hardening).
