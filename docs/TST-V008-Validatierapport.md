# TST-V008 — Validatierapport

| Veld | Waarde |
|------|--------|
| Build label | V008 |
| Datum | 2026-06-13 |
| Vorige build | V007 |
| Kritieke bevindingen | 0 |

Deze sessie leverde de **volledige uitwerking van ADR-022 — beoordelingsprofiel/checklist per
componenttype** (Fase A–F + Wijziging W1), plus een dev-infraverbetering:

- **Fase A** (`9eb8310`, migratie `0007`): generiek `component_profiel` (shared-PK), `lifecycle_status`
  verhuisd van `applicatie` → profiel, `checklistvraag` surrogate-PK + `componenttype`, kind-FK-retarget.
- **Fase B** (`48a3671`): engine-generalisatie — `aantal_vragen` per componenttype (+ `actief`).
- **Fase C** (`05bdfcb`): toestand-gebaseerde type-lock (`SUBTYPE_HEEFT_DATA`), `type_wijzigbaar`-capability,
  read-only "wat verdwijnt"-samenvatting.
- **Wijziging W1** (`b6ee8cf` doc, `d530010` impl, migratie `0008`): `checklistvraag`/`_optie`
  **tenant-scoped** (RLS), volledige tenant-CRUD via `cd_app`, in-tenant fan-out, optie-beheer verhuisd
  van platform naar tenant-facing. Lost de cross-tenant fan-out-knoop structureel op.
- **Scoringslijst-actief** (`dd3ec6b`): scoring-read filtert op `actief=true` (byte-identiek aan de engine-set).
- **Dev hot-reload** (`2681637`): `cd-api` draait lokaal met `uvicorn --reload` (reload-dirs `/app`+`/modules`);
  neemt de "stale worker"-ruis weg. Dockerfile-CMD (prod) ongemoeid.
- **Fase E** (`2a71ec1`, migratie `0009`): **tweede checklist-dragend componenttype** end-to-end —
  `checklist_dragend`-catalogusvlag, generieke profiel-creatie, type-generieke scoring + "start beoordeling".
- **Fase F** (`5ac30d6`): readiness-dashboard **per type** uitgesplitst (Besluit 3); `recent_gewijzigd`
  type-generiek.

## Backend — 4 assen (CONTRIBUTING.md §6)

| As | Commando | Verwacht | Resultaat |
|----|----------|----------|-----------|
| 1 — py_compile | `find backend modules -name '*.py' \| xargs py_compile` | 0 syntaxfouten | **Geslaagd** — 0 fouten |
| 2 — pytest | `pytest modules/` + `backend/tests/` | alle groen | **Geslaagd** — **567** module + **71/72** platform (1 pre-existing env-test, zie onder) |
| 3 — Alembic | `alembic heads` / `branches` | 1 head, 0 branches | **Geslaagd** — 1 head `0009_adr022_e_checklist_dragend`, 0 branches |
| 4 — referentie-grep | grep `Eraneos\|compliman\|cm_` | 0 hits in code | **Geslaagd** — 0 hits in `backend`/`modules`/`frontend/src` (matches alleen in eerdere TST-rapporten die het patroon citeren) |

## Frontend — poorten

| Poort | Verwacht | Resultaat |
|-------|----------|-----------|
| `vite build` | 0 fouten | **Geslaagd** — built in ~0,3 s, 0 fouten |
| `vitest run` | alle groen | **Geslaagd** — **255 passed** (35 bestanden) |

## Empirische live-verificaties deze sessie

| Onderdeel | Verificatie | Resultaat |
|-----------|-------------|-----------|
| Migraties `0007`/`0008`/`0009` | up → down → up tegen de live cd_admin-DB | Groen |
| W1 fan-out | vraag toevoegen/(de)activeren → in-tenant lifecycle-herberekening, geen stale-venster | Groen (`test_vraagbeheer_w1_fanout`) |
| Scoringslijst-actief | scoring-read == engine-set; gedeactiveerde vraag eruit, score-historie behouden | Groen (`test_scoringlijst_actief_w1`) |
| Fase E tweede type | `saas_dienst`-component: profiel → start → scoren → `migratieklaar`/`geblokkeerd`; type-scoping | Groen (`test_tweede_type_lifecycle_e`) |
| Fase F per-type readiness | live dashboard: Applicatie 4/12 + Applicatieserver 1/2 `migratieklaar`, gescheiden rollups | Groen |
| cd-api hot-reload | WatchFiles-reload op `/modules`-wijziging zonder handmatige recreate | Groen |

## Bekende afwijking (geen kritiek)

`test_auth_pkce.py::test_callback_succes_zet_cd_session_cookie` faalt **omgevingsgebonden**
(Secure-cookievlag in test/dev) — faalt identiek op een schone `HEAD`, staat los van ADR-022.
Geparkeerd in OPVOLGPUNTEN.md (d). **0 kritieke bevindingen** in scope.
