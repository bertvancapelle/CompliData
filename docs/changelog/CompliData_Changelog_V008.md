# CompliData Changelog V008

**Datum**: 2026-06-13

## Wijzigingen

Sessie bovenop V007: **ADR-022 — beoordelingsprofiel/checklist per componenttype** volledig
afgerond (Fase A–F + Wijziging W1), plus een dev-infraverbetering. Kernlijn: een componenttype
kan nu een eigen, **tenant-eigen** checklist dragen — met profiel, scoring, lifecycle, type-lock en
**per-type readiness** — volledig losgekoppeld van `applicatie`.

### ADR-022 — beoordelingsprofiel per componenttype

- **Fase A** (`9eb8310`, migratie `0007`) — generiek **`component_profiel`** (shared-PK met
  `component`) als engine-state-drager; `lifecycle_status` verhuisd van `applicatie` → profiel.
  `checklistvraag` naar surrogate UUID-PK + `componenttype`-discriminator; kind-FK's
  (`checklistscore`, `checklistvraag_optie`) geretarget naar `checklistvraag.id`;
  `checklistscore`/`blokkade` herankerd op `component_id` (→ `component_profiel`).
- **Fase B** (`48a3671`) — engine-generalisatie: `aantal_vragen` wordt **per componenttype** geteld
  (en sinds W1 óók `actief`); lege vragenset → `in_inventarisatie`; type-bewuste vraagvalidatie.
- **Fase C** (`05bdfcb`) — **toestand-gebaseerde type-lock**: statische `SUBTYPE_BESCHERMD`-guard
  vervangen door een transactie-lokale "gevuld?"-evaluatie (`SUBTYPE_HEEFT_DATA`, 422);
  `type_wijzigbaar`-capability; read-only "wat verdwijnt"-samenvatting.
- **Wijziging W1** (`b6ee8cf` doc, `d530010` impl, migratie `0008`) — **tenant-eigendom van de
  vragenset**: `checklistvraag`/`_optie` tenant-scoped (RLS + FORCE, composiet-FK
  `(tenant_id, checklistvraag_id)`), volledige tenant-CRUD via `cd_app`, **in-tenant fan-out**
  (atomair, geen cross-tenant write/BYPASSRLS), optie-/vraagbeheer verhuisd van platform
  (`/platform/checklistconfig`) naar tenant-facing (`/checklistconfig`); RBAC-entiteit
  `CHECKLISTVRAAG` naar het inhoud-patroon; soft-deactivatie via `checklistvraag.actief`;
  `platform_init` laat de checklist-seed los, `dev_seed` seedt de baseline per tenant.
- **Scoringslijst-actief** (`dd3ec6b`) — de scoring-read (`/checklistvragen`) filtert op
  `actief=true`, byte-identiek aan de set die de engine voor `aantal_vragen` telt; gedeactiveerde
  vragen vallen uit de lijst, bestaande scores blijven historie.
- **Fase E** (`2a71ec1`, migratie `0009`) — **tweede checklist-dragend componenttype** end-to-end:
  `componentconfig_optie.checklist_dragend`-vlag (de enige bron), generieke profiel-creatie zonder
  subtype, **type-generieke "start beoordeling"** (`concept → in_inventarisatie` op profiel-niveau;
  `applicatie` delegeert), type-gescopete scoring-read, scoring-UI component-generiek op het
  component-detail. Dev-seed: `applicatieserver` als tweede checklist-dragend type.
- **Fase F** (`5ac30d6`) — readiness-dashboard **per type** uitgesplitst (Besluit 3): de gefuseerde
  `lifecycle_telling` vervangen door `readiness_per_type` (statusverdeling + "n van m migratieklaar"
  per type); `recent_gewijzigd` type-generiek. Geen migratie.

### Dev-infra

- **Hot-reload** (`2681637`) — `cd-api` draait lokaal met `uvicorn --reload` (één worker,
  reload-dirs `/app`+`/modules`); neemt de terugkerende "stale worker"-ruis weg. De prod-default
  (Dockerfile-CMD `--workers 2`, geen reload) en de init-/migrate-container blijven ongemoeid.

## Migraties

`0007` (component_profiel + lifecycle-verhuizing), `0008` (tenant-scoped vragenset), `0009`
(`checklist_dragend`-vlag). Head: `0009_adr022_e_checklist_dragend`.

## Teststatus

567 backend-module + 72 platform (1 pre-existing env-auth-test, omgevingsgebonden) + 255 frontend
groen. 0 kritieke bevindingen. Zie `docs/TST-V008-Validatierapport.md`.
