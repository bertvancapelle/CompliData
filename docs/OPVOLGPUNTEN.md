# CompliData — Opvolgpunten (backlog)

Bijgehouden met de hand. Niet door `gen_build.py` gegenereerd.
Bron: sessie 2–3 (P1–P5, OP-9 t/m OP-12). Status per punt expliciet vermeld.

---

## OPEN

### OP-3 — Refresh-token-subsysteem (uit P2) — OPEN

P2 zet bewust geen refresh-token; sessie verloopt na 15 min en vereist
opnieuw inloggen. Bouwen: `/auth/refresh`, veilige server-side opslag van de
refresh-token gekoppeld aan een sessie-id, rotatie/intrekking, koppeling aan
de 8-uurs refresh-grens (CLAUDE.md). Geen token client-leesbaar.

### OP-4 — RP-initiated logout via Keycloak (uit P2) — OPEN

`auth/logout` wist nu alleen de lokale `cd_session`-cookie; de Keycloak-SSO-
sessie blijft staan, waardoor een volgende `/login` stil kan herinloggen.
Aanvulling: Keycloak end-session-endpoint aanroepen bij logout.

### OP-6 — Resource-ownership binnen tenant (P5/ADR-010) — AFGEDEKT (fase 1, P5)

Afgedekt voor fase 1 — tenant-scoped record-resolutie (kruis-tenant → 404) +
rol + RLS volstaan; per-gebruiker-eigenaarschap niet nodig in fase 1
(collaboratief register, ADR-009).

Geïmplementeerd in P5 (Applicatie-CRUD, referentie voor de overige entiteiten):
record-resolutie strikt binnen de tenant-sessie (RLS + expliciete
`tenant_id`-filter); een id buiten de tenant is niet vindbaar ⇒ HTTP 404
`NIET_GEVONDEN` (geen 403, geen onderscheid "bestaat niet" vs "andere tenant",
dus geen lek). Binnen de tenant geldt rol-gebaseerde autorisatie via
`vereist_permissie`; elke Medewerker/Beheerder mag elk record in de eigen tenant
bewerken. Fijnmazig per-gebruiker-eigenaarschap is bewust uitgesteld en pas te
heroverwegen als een toekomstige eis daarom vraagt.

### OP-7 — 401 en 403 in hetzelfde foutformaat (uit P3) — OPEN

403 gebruikt het canonieke `{"fout":{...}}`-formaat; 401 volgt nog het
bestaande `{"detail":{"code":...}}`-patroon van de auth-laag. Op termijn beide
gelijktrekken naar `{"fout":{...}}`.

### OP-13 — Platform-tabel-grants Platforminstellingen/Platformmetadata — OPEN

Het platform-permissiedomein (ADR-012) kent `Platforminstellingen` en
`Platformmetadata`, maar alleen de `tenant`-tabel bestaat. Bij het bouwen van
die endpoints: tabellen + migratie + `GRANT … TO cd_platform` /
`REVOKE … FROM cd_app` (zelfde patroon als `tenant`).

### OP-14 — Dev-credentials vervangen vóór productie — OPEN

`changeme_dev` staat als dev-default in realm (client-secret + testgebruikers)
en DB-rollen (cd_app/cd_platform/cd_admin via `POSTGRES_PASSWORD`). Vóór
productie vervangen door secrets; testgebruikers verwijderen of scheiden van
productie-realm.

### OP-15 — CLAUDE.md "test-mode auth stub/auto-seed" is onjuist — OPEN

De CLAUDE.md-comment "Backend (test mode — auth stub, auto-seed)" klopt niet:
`COMPLIDATA_TEST_MODE` versoepelt alleen de Origin-check + rate-limit-sleutel; er is
géén auth-stub en géén auto-seed. Inloggen vereist altijd Keycloak. CLAUDE.md
rechtzetten (V003-bevinding, `docs/LOKAAL-TESTEN.md`).

### OP-16 — `tenantSlug`-getter leest verkeerd veld — OPEN

`frontend/src/store/auth.js` `tenantSlug` leest `user.tenant_slug`, maar `/auth/me`
geeft `tenant_id` → altijd `null`. Raakt `useTheme`/per-tenant-thema's zodra die
gebouwd worden.

### OP-17 — ADR-009 enum-voetnoten ↔ code synchroniseren — OPEN

ADR-009 markeert enums als "voorgesteld"; de code (single source `models.py`) wijkt
af en is leidend: `hostingmodel` = 7, `migratiepad` = 6, `protocol` = enum,
`checklist_compleet` transient (ADR-013). ADR-009-tekst bijwerken.

### OP-18 — Stale V001-docs (IMPLEMENTATIEPLAN / SESSIE_BRIEFING) — OPEN

`IMPLEMENTATIEPLAN.md` en `SESSIE_BRIEFING.md` bevatten V001-snapshots die niet meer
de werkelijke bouwstatus weerspiegelen. Actualiseren of als historisch markeren.

### OP-19 — Frontend bundle >500 kB — OPEN

De productie-bundle overschrijdt 500 kB (PrimeVue DataTable). Route-level
lazy-loading / code-splitting als optimalisatie.

---

## AFGEROND (sessie 2–3)

- **OP-1** — platform_init-seed als deploystap → vervangen door de
  init-container (ADR-011): `cd-migrate` migreert (cd_admin) → `platform_init`
  → sluit af, met gating vóór de app. CLAUDE.md Commands bijgewerkt.
- **OP-2** — plantekst + skills bijgewerkt → §Architectuurcorrectie in
  `IMPLEMENTATIEPLAN.md` gecorrigeerd; `platform_init`/deploypatroon in
  complidata-db/-security/-tests vastgelegd.
- **OP-5** — cookie-attributen settings-driven (`cookie_secure`/`samesite`/
  `domain`) bevestigd; `COOKIE_SECURE=false` voor lokaal http (P4).
- **OP-8** — CONTRIBUTING §6 As 2 gecorrigeerd naar
  `python3 -m pytest backend/tests/ modules/` (groen geverifieerd).
- **OP-9** — deploy-/migratiestrategie vastgelegd in **ADR-011** (init-container).
- **OP-10** — OIDC `redirect_uri` gelijkgetrokken (realm ↔ backend) +
  realm-import (`--import-realm`); login-round-trip werkt.
- **OP-11** — `cd_admin` volledig uit de app-laag; `cd_platform` (non-superuser)
  voor platform-endpoints (ADR-012).
- **OP-12** — rol-mapping/tweelaags rollenmodel → opgegaan in **ADR-012**
  (realm-rollen → `realm_access.roles`, platform- + tenant-domein).
