# ADR-012 — Tweelaags rollenmodel: platform- en tenant-rollen met strikte scheiding

| | |
|---|---|
| **Status** | Aanvaard |
| **Datum** | 2026-06-06 |
| **Beslissers** | Bert van Capelle (G. van Capelle Beheer B.V.) |
| **Gerelateerd** | ADR-002 (IAM/Keycloak), ADR-003 (multi-tenant RLS), ADR-010 (tenant-RBAC), ADR-011 (init-container) |

## Context

LIKARA kent twee fundamenteel verschillende soorten handelingen:

1. **Tenant-werk** — inhoudelijk werken binnen één tenant (applicaties,
   checklists, koppelingen), afgeschermd door Row Level Security (ADR-003) en
   de tenant-RBAC uit ADR-010 (`viewer/medewerker/beheerder/auditor`).
2. **Platform-werk** — handelingen bóven de tenants: een tenant aanmaken/
   onboarden, platforminstellingen beheren, platform-metadata en
   systeem-audit inzien. Dit heeft geen tenant-context en mag geen
   inhoudelijke tenantdata raken.

Drie problemen dwingen een expliciete beslissing af:

- De geïmporteerde Keycloak-realm bevatte 17 rollen uit een ander product
  (CompliMan: `R-DIR`…`R-SDM`) die niet op het LIKARA-autorisatiemodel
  aansluiten.
- Tenant-aanmaak is een platform-handeling, maar er was geen rol/permissie-
  domein dat dit afdekt zonder tenant-context.
- De applicatie gebruikte `lk_admin` (superuser) in de app-laag
  (`get_admin_session`, OP-11) — een schending van least privilege, want
  `lk_admin` omzeilt RLS.

## Besluit

### B1 — Twee strikt gescheiden accounttypes

Een account is **óf platform óf tenant, nooit beide**.

- **Platform-rollen** (geen tenant-context):
  - `platformbeheerder` — volledige CRUD op Tenant + Platforminstellingen,
    lezen van Platformmetadata.
  - `platformoperator` — **uitsluitend lezen** van platform-metadata (dat een
    tenant bestaat, status, gebruiks-/health-metrieken, systeem-audit). Geen
    inhoudelijke tenantdata, geen mutatie.
- **Tenant-rollen** (binnen één tenant, onder RLS — ongewijzigd t.o.v.
  ADR-010): `viewer`, `medewerker`, `beheerder`, `auditor`.

### B2 — Twee gescheiden permissiedomeinen

Het platform- en het tenant-permissiedomein zijn losse bronnen van waarheid
met losse guards. Platform-endpoints checken **alleen** platform-rollen en
openen **alleen** een platform-sessie; tenant-endpoints checken **alleen**
tenant-rollen en draaien **alleen** onder `get_session(tenant_id)` met RLS.
Een rol uit het ene domein kan een endpoint in het andere domein **nooit**
bedienen (kruis-toegang ⇒ 403).

### B3 — DB-driedeling (least privilege)

| Rol | Type | Gebruik |
|---|---|---|
| `lk_admin` | superuser | **Uitsluitend** de init-container (migratie + seed, ADR-011). |
| `lk_platform` | non-superuser (NIEUW) | Platform-endpoints in de app (tenant-provisioning, platforminstellingen). Géén superuser, géén RLS-bypass-noodzaak. |
| `lk_app` | non-superuser | Tenant-gescopet werk onder RLS. |

Gevolg: **`lk_admin` verdwijnt volledig uit de app-laag** (OP-11 opgelost).

### B4 — Realm op LIKARA afstemmen

De 17 CompliMan-rollen worden uit de realm verwijderd; er komen 6
LIKARA-realm-rollen (4 tenant + 2 platform). De rollen-mapper schrijft
naar `realm_access.roles` (zodat de backend ze leest); per rol komt er een
dev-testgebruiker, met respect voor de strikte scheiding (een gebruiker
krijgt óf platform- óf tenant-rollen).

## Gevolgen

- **Security/least privilege**: `lk_admin` heeft een minimaal blootstellings-
  vlak (alleen init-container); de app draait met `lk_app` (RLS) en
  `lk_platform` (platform, non-superuser). OP-11 is hiermee opgelost.
- **Scheiding van zorg**: een platformoperator ziet metadata, nooit
  inhoudelijke tenantdata; tenant-isolatie (RLS) blijft volledig intact en
  staat náást de RBAC-laag.
- **Realm-opschoning**: de realm weerspiegelt voortaan het LIKARA-model;
  CompliMan-rollen verdwijnen.
- **Gefaseerde invoering**: ADR (dit), `lk_platform` + lk_admin-verwijdering,
  realm, platform-permissiedomein/guard, en tenant-onboarding-endpoints
  worden in losse, afzonderlijk te valideren stappen ingevoerd.

## Alternatieven overwogen

- **Combineerbare rollen (één account met platform- én tenant-rollen)**:
  verworpen — vervaagt de scheiding, vergroot het risico dat een platform-rol
  per ongeluk tenantdata raakt; strikte scheiding is eenvoudiger te
  verifiëren en fail-secure.
- **Één gedeelde permissietabel voor beide domeinen**: verworpen — koppelt de
  domeinen en maakt kruis-toegang mogelijk; twee losse bronnen sluiten dat
  structureel uit.
- **`lk_admin` in de app-laag houden** (status quo): verworpen — superuser
  omzeilt RLS; onaanvaardbaar blootstellingsvlak voor een langdraaiend proces
  (OP-11).
- **Tenant-aanmaak als losse CLI/handmatige stap**: verworpen — onboarding is
  een herhaalbare, geautoriseerde platform-handeling die via een endpoint met
  `platformbeheerder`-autorisatie en audit hoort te lopen, niet buiten de app
  om.
