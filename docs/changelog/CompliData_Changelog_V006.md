# CompliData Changelog V006

**Datum**: 2026-06-10

## Wijzigingen

Sessie CD025–CD038 bovenop V005:

### ADR-019 — configureerbaar antwoordveld per checklistvraag (fasen 2A–2E + dev-seed)

- **2A (CD027)** — datamodel + migratie `0003_antwoordconfig` + seed: `AntwoordType`-enum,
  `antwoordtype` op `ChecklistVraag`, optie-catalogus `checklistvraag_optie` (stabiel
  `optie_sleutel`, soft-deactivate via `actief`, `afgeleid_bron`), `antwoord_waarde` (jsonb,
  nullable) op `Checklistscore`. 27 getypeerde vragen / 96 opties; afgeleid 2.1 ← `HostingModel`,
  12.1 ← `NiveauEnum`. R2-grants (cd_app SELECT-only catalogus, cd_platform CRUD).
- **2B (CD028)** — backend read/write + validatie: structureel in Pydantic (422 native);
  semantisch tegen de catalogus in de service → `OngeldigAntwoord` (422-envelope). Engine
  byte-identiek (alleen `score` voedt lifecycle/blokkade).
- **2C (CD029)** — scoring-UI: antwoordcontrole per type (select/checkboxes/getal) in de
  CD025-uitklaprij; kolomkop "Score" → **"Afgehandeld"**; opslaan zonder `score`.
- **2D (CD031)** — platform-config-endpoints `/platform/checklistconfig` + RBAC
  (ADR-012 Addendum A); orphan-bescherming (antwoordtype alleen vanuit `geen`), afgeleide sets
  read-only, soft-deactivate (geen hard delete).
- **2E (CD032–CD034)** — `GET /auth/platform/me`; sessietype-bewuste SPA-auth + lichte
  beheer-shell (`BeheerLayout`, `routeBeslissing`); beheer-UI `ChecklistConfigBeheer`.
- **Dev-seed (CD030)** — `antwoord_waarde` op de 256 getypeerde gescoorde rijen; 2.1 = werkelijk
  hostingmodel van de app.

### Hardening-bundel (CD035–CD038)

- **O2 (CD035)** — 7.5 BIO2-classificatie → **BBN1/2/3** via expand/contract: seed (fresh) +
  migratie `0004_bio2_bbn` (soft-deactivate legacy L/M/H op bestaande DB's). Bestaande antwoorden
  resolvebaar; engine ongemoeid.
- **OP-16 (CD036)** — geverifieerd reeds gefixt (`tenantId`-getter leest `tenant_id`).
- **OP-7 (CD037)** — geverifieerd reeds canoniek (401 = `{"fout":{…}}`, CD005); stale docstrings
  recht + lock-test.
- **OP-4 (CD038)** — geverifieerd reeds geïmplementeerd (RP-initiated logout, CD008/CD010); stale
  AppLayout-comment recht.

### Backlog-sweep (read-only)

- **OP-19** — bundle >500 kB: gemitigeerd (grootste chunk 384 kB, route-lazy-loading actief).
- **OP-13/20/21/22** — tegen de code geverifieerd, blijven open (OP-21 optioneel, OP-22 bewust
  geaccepteerd dev-risico).

**ADR's**: **ADR-019** (Aanvaard) + **ADR-012 Addendum A** (`PlatformEntiteit.CHECKLISTCONFIG`,
Aanvaard) toegevoegd aan `docs/adr/`.

**Migraties**: `0003_antwoordconfig` (additief), `0004_bio2_bbn` (data, soft-deactivate). 1 head.

**Tests**: **519 backend + 151 frontend** groen · 0 kritieken.

**Open / vooruit**: OP-13 (platform-instellingen/-metadata bij die endpoints), OP-20 (live
NULLS-LAST, nu deels goedkoop te sluiten), OP-21 (optioneel), OP-22 (pre-productie, mogelijk
ADR-waardig); geparkeerd OP-3 + Keycloak `revokeRefreshToken` (eigen analyse-gate) en OP-14
(deploy/secrets); observaties O3/O4 open.
