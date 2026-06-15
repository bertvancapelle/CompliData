# TST-V009 — Validatierapport

| Veld | Waarde |
|------|--------|
| Build label | V009 |
| Datum | 2026-06-14 |
| Vorige build | V008 |
| Kritieke bevindingen | 0 |

Deze sessie leverde **twee volledig afgeronde + gelande architectuurtrajecten**:

- **ADR-006 audit-trail (checkpoint #17) — VOLLEDIG af + GELAND** (`6eb0699`, migratie `0010`):
  append-only `audit_log` (tenant-scoped) + `platform_audit_log`, FORCE RLS, append-only grant met
  `REVOKE ALL` + `BEFORE UPDATE/DELETE/TRUNCATE`-trigger, capture-hook (`before/after_flush`, ORM-only),
  actor via ContextVar (+ `system:dev_seed`/`platform_init`), per-tenant SHA-256 hash-keten met
  `pg_advisory_xact_lock`-serialisatie (fork uitgesloten), blokkade-classificatie gesplitst
  `derive`/`update`, lees-API `GET /auditlog` + RBAC `AUDITLOG`, capture-grens-invariant.
- **ADR-023 ArchiMate-uitlijning — CUTOVER (Fase A + B) af + GELAND** (`038f100`, 57 bestanden,
  live-geverifieerd op verse DB). Migratieketen t/m **0017**: element-supertype (shared-PK) +
  ArchiMate-typing-catalogus (0011); één getypeerd `relatie`-model (0012); element-promotie
  datatype/gebruikersgroep/contract (0013); cutover koppeling→flow (0014), component_structuur→
  assignment/aggregation (0015), component_contract→association (0016), datatype/gebruikersgroep-band→
  access/serving + drop `applicatie_id` + CASCADE-wijziging Besluit 13 (0017). Oude tabellen gedropt;
  impact-graaf type-bewust herbouwd.

## Backend — 4 assen (CONTRIBUTING.md §6)

| As | Commando | Verwacht | Resultaat |
|----|----------|----------|-----------|
| 1 — py_compile | `find backend modules -name '*.py' \| xargs py_compile` | 0 syntaxfouten | **Geslaagd** — 0 fouten |
| 2 — pytest | `pytest backend/tests/` + `modules/` | alle groen | **Geslaagd** — **651 passed / 1 pre-existing env-test** (652 totaal, 0 skipped) |
| 3 — Alembic | `alembic heads` / `branches` | 1 head, 0 branches | **Geslaagd** — 1 head `0017_adr023_cutover_band`, 0 branches |
| 4 — referentie-grep | grep `eraneos\|compliman\|cm_` | 0 hits in code | **Geslaagd** — 0 hits in `backend`/`modules`/`frontend/src` |

## Frontend — poorten

| Poort | Verwacht | Resultaat |
|-------|----------|-----------|
| `vitest run` | alle groen | **Geslaagd** — **255 passed** (35 bestanden) |

## Empirische live-verificaties deze sessie (verse DB, alembic = 0017)

| Onderdeel | Verificatie | Resultaat |
|-----------|-------------|-----------|
| Reset + migratieketen | `down -v && up -d` → init migreert t/m `0017` + platform_init (17 catalogus-opties: 7+2+8) | Groen |
| Datamigratie-equivalentie | koppeling→flow (10), component_structuur→assignment (3), component_contract→association (11); oude tabellen gedropt | Groen (1-op-1) |
| Richting per slice | flow kenmerken `{protocol, richting, impact_bij_verbreking}`; assignment host→gehoste; association `relatie_rol` | Groen |
| Impact/structuur end-to-end | gedeelde infra Oracle FIN-DB → {Belastingsysteem, Financieel}; type-bewuste `impact_analyse` | Groen |
| RLS + composiet-FK cross-tenant | tenant B ziet 0; cross-tenant relatie-insert → `violates fk_relatie_bron_element` | Groen |
| CASCADE + wees-detectie | wees-query (element zonder relatie) functioneel | Groen |
| Append-only audit | `cd_app` op `audit_log`: `permission denied` voor UPDATE én DELETE | Groen |

## Twee mechanische live-stop-fixes (meegegaan in `038f100`)

- Revisie-ID `0016` ingekort tot `0016_adr023_cutover_contract` (<32 tekens; `alembic_version` is
  `varchar(32)`).
- `seed_componentconfig.bouw_componentconfig()`: uniforme dict-sleutelset per rij (multi-row
  `pg_insert` eist het) — **waarden byte-identiek**.

## Bekende afwijking (geen kritiek)

`test_auth_pkce.py::test_callback_succes_zet_cd_session_cookie` faalt **omgevingsgebonden**
(Secure-cookievlag in test/dev) — faalt identiek op een schone `HEAD`, staat los van ADR-006/ADR-023.
Geparkeerd in OPVOLGPUNTEN.md. **0 kritieke bevindingen** in scope.

## Niet-blokkerende bevinding — test-teardown-residu

Live-integratietests laten 11 `element`-supertype-rijen achter (subtype + relatie wél opgeruimd; de
in ADR-023 nieuwe supertabel niet). Productiecode is correct (services verwijderen via element-cascade).
Een `down -v`-reset wist het residu. Follow-up: teardowns via het element laten verwijderen.
