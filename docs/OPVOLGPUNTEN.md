# CompliData — Opvolgpunten (backlog)

Bijgehouden met de hand. Niet door `gen_build.py` gegenereerd.
Bron: sessie 2 (P1–P3). Status per punt: **OPEN** tenzij anders vermeld.

---

## Hoog

### OP-1 — platform_init seed als expliciete deploystap (uit P1)

`seed_checklist_vragen()` draait nu via `python3 -m app.platform_init`, NA
`alembic upgrade head` (Optie B). Dit is een aparte stap; zonder die stap is
een live DB leeg (geen 89 checklistvragen).

Borgacties:
- Opnemen in de Commands-sectie van CLAUDE.md.
- Toevoegen aan de docker-entrypoint zodat het automatisch draait na de
  migratie.
- Onderdeel maken van de P4 live-verificatie ("seed: 89 vragen aanwezig"
  vereist dat `platform_init` is gedraaid).

### OP-3 — Refresh-token-subsysteem (uit P2)

P2 zet bewust geen refresh-token; sessie verloopt na 15 min en vereist
opnieuw inloggen. Bouwen: `/auth/refresh`, veilige server-side opslag van de
refresh-token gekoppeld aan een sessie-id, rotatie/intrekking, koppeling aan
de 8-uurs refresh-grens (CLAUDE.md). Geen token client-leesbaar.

---

## Midden

### OP-4 — RP-initiated logout via Keycloak (uit P2)

`auth/logout` wist nu alleen de lokale `cd_session`-cookie; de Keycloak-SSO-
sessie blijft staan, waardoor een volgende `/login` stil kan herinloggen.
Aanvulling: Keycloak end-session-endpoint aanroepen bij logout.

### OP-5 — Cookie-attributen uit settings bij login/callback (uit P2, P4)

Verifieer bij P4 dat de `cd_session`-cookie zijn attributen uit settings haalt
(`cookie_secure` / `cookie_samesite` / `cookie_domain`, net als logout), zodat
lokaal/test over http daadwerkelijk inlogbaar is; hardcoded `Secure` zou dat
lokaal breken.

### OP-6 — Resource-ownership binnen tenant (uit P3, koppelen aan P5/ADR-010)

De RBAC-guard checkt entiteit × actie; fijnmazig eigenaarschap (mag deze
gebruiker DIT specifieke record) zit er nog niet in. Tenant-isolatie is al via
RLS afgedekt; voeg record-niveau-ownership toe zodra dat nodig is bij de
module-CRUD (P5).

### OP-7 — 401 en 403 in hetzelfde foutformaat (uit P3)

403 gebruikt het canonieke `{"fout":{...}}`-formaat; 401 volgt nog het
bestaande `{"detail":{"code":...}}`-patroon van de auth-laag. Op termijn beide
gelijktrekken naar `{"fout":{...}}`.

---

## Laag / documentatie

### OP-2 — Plantekst + skills bijwerken (uit P1, bij sessie-einde)

- `docs/IMPLEMENTATIEPLAN.md` §Architectuurcorrectie zegt dat de seed
  "momenteel als tenant-seeddata wordt aangeroepen"; dat klopt niet meer (de
  seed was nergens bedraad). Tekst corrigeren.
- `platform_init`-seedpatroon vastleggen in de complidata-backend/-db skill
  (skill-review, stap 3 van het afsluitpatroon).

### OP-8 — CONTRIBUTING.md §6 doc-drift

§6 schrijft `cd backend && pytest modules/` voor, maar `modules/` staat in de
repo-root, waardoor dat commando faalt. Corrigeren naar het werkende commando
(pytest vanaf repo-root, bv. `python3 -m pytest backend/tests/ modules/`).
