# CompliData Changelog V007

**Datum**: 2026-06-12

## Wijzigingen

Sessie CD039–CD058 bovenop V006:

### ADR-020 — leverancier-/contractregister (CD039–CD046)

- **CD039–040** — ADR-020 + datamodel: vijf tenant-scoped tabellen (leverancier, contract,
  applicatie↔contract-koppeling, …) met RLS + FORCE, CHECK/UNIQUE-invarianten (mantel/deel,
  leverancier-erving), platform-brede `contractconfig`-catalogus (geen RLS). Live geverifieerd
  (14 checks: RLS-isolatie, grants, CHECK/UNIQUE).
- **CD041–043** — CRUD + invarianten + platform-config + tenant-UI (leverancier-/contractlijsten,
  -detail, -formulieren); rol-gating.
- **CD044–045** — overzichten (deelcontracten-dekking, lifecycle, datums) + **categorie-8-
  contextpaneel** (read-only registratie in ApplicatieDetail; voedt de engine niet). Browser-
  walkthroughs groen.
- **CD046** — catalogus-beheer-UI (`ContractConfigBeheer`) + dev-seed contractregister.

### Incidenten + ZoekSelect (CD047–CD049)

- **CD047/048** — RLS-poolcontext-fix: tenant-context **transactie-lokaal**
  (`set_config(..., true)` via een `after_begin`-hook op RLS-sessies; `pool_pre_ping=True`).
  Lost het 500-na-commit op (contextloze poolverbinding bij `commit`→`refresh`). Live:
  koude-pool-burst 6×201, cross-tenant-wisseltest, context-isolatie groen.
- **CD049** — `ZoekSelect.vue`: server-side zoekende combobox voor onbegrensd groeibare
  entiteit-referentievelden (debounce, ~10 + verfijn, combobox-a11y).

### ADR-021 — component-herfundering (CD050–CD054, CD056)

- **CD050–051** — herfundering: supertype `component` + subtype `applicatie` als **shared-PK**
  (Optie 2; read-only proxy-properties houden de API byte-compatibel); landschapsgraaf
  (`component_structuur` + koppeling- en contract-generalisatie). `0006_component_herfundering`.
- **CD052–053** — component-/structuur-CRUD; **COMPONENTCONFIG**-catalogus (componenttype +
  structuurrelatie_type; systeem-sleutel `applicatie` niet deactiveerbaar).
- **CD054 (incl. v2)** — verenigde Componenten-UI: padconsolidatie, besturingskolommen,
  **convergente aanmaak** (type applicatie maakt atomair het subtype), **menu-sanering**
  (`/applicaties` → redirect). Commits: `8f44aff` (CD054b-v2). Browser-walkthrough groen.
- **CD056** — impactanalyse: read-only afhankelijkheids-traversal (cyclus-veilige BFS, niveau +
  pad + readiness-/contractcontext) op ComponentDetail/ApplicatieDetail. Commit `97a48cb`.

### Infra — Keycloak-scheiding (CD055)

- **CD055** — Keycloak eigen database `keycloak` (rol `kc_user`) + **named volume** voor
  Postgres. Lost de `COMPONENT`-naamruimte-collision op en houdt Keycloak-secrets uit de
  `complidata`-dump → **OP-22 gesloten**. Reset-proof (2× `down -v && up -d`) bewezen.
  Commit `a733039`.

### Borging + afsluiting (CD057–CD058)

- **CD057** — kennisborging: skill-V007-secties, CLAUDE.md-werkprotocollen (triggerdiscipline,
  walkthrough, gerichte-staging), ADR-022-voorbereiding, ADR-021-realisatienotitie,
  OPVOLGPUNTEN-sweep (OP-22 gesloten, OP-23..OP-27). Commit `fb130df`.
- **CD058** — sessie-afsluiting V006→V007 (dit document, TST-V007, NEXT_SESSION, OP-28, V-bump).

**ADR's**: **ADR-020** (contractregister), **ADR-021** (component-herfundering, incl. W1 +
shared-PK-realisatie), **ADR-022 (voorbereiding)** — checklist per componenttype.

**Migraties**: `0006_component_herfundering`. 1 head, 0 branches.

**Tests**: **631 backend + 239 frontend** groen · 0 kritieke bevindingen.

**Open / vooruit**: ADR-022-afpelling (start volgende sessie), ADR-006 (audit-trail), #16
user-/tenantmanagement → #15, #14 na ADR-006; OP-28 (VPS) t.z.t.; OP-3/13/20/21 en OP-23..OP-27
als achtergrond.
