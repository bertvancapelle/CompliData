# TST-V010-Validatierapport

**Build**: V010
**Datum**: 2026-06-15
**Sessie**: DC009
**Migratie head**: `0021_adr023_deliverable`

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `py_compile` op alle Python-bestanden (excl. node_modules/.git/__pycache__/.claude) | **Geslaagd** — 0 syntaxfouten |
| 2 — Tests | `pytest backend/tests/ modules/ -q` | **Geslaagd** — 692 passed |
| 3 — Database-integriteit | `alembic heads` / `alembic branches` | **Geslaagd** — 1 head (`0021_adr023_deliverable`), 0 branches |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/frontend/modules/docs/adr | **Geslaagd** — 0 hits |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` | **Geslaagd** — 258 passed (35 files) |
| `vite build` | **Geslaagd** — 0 fouten |

## Aantal kritieken

**0.**

## Geaccepteerde afwijkingen

- **Pre-existing env-test** `test_auth_pkce.py::test_callback_succes_zet_cd_session_cookie`:
  omgevingsgebonden (Secure-cookievlag in test/dev), DB-onafhankelijk. In de huidige omgeving **groen**
  (30 passed). Staat los van de DC009-wijzigingen; niet als regressie behandeld.

## Invariant-borging

- **Score blijft de enige lifecycle-driver**: voor elke nieuwe Fase-E-entiteit (plateau/work_package/
  deliverable) is dit machine-geborgd via (a) een offline import-afwezigheidstest (de service importeert
  geen `lifecycle_service`/`herbereken_lifecycle`/`ComponentProfiel`/`Blokkade`/`Checklistscore`) en
  (b) een live test (de entiteit/koppeling doet geen `component_profiel`/lifecycle ontstaan).
- **Live-test-residu**: 0 — de live element-subtype-tests ruimen hun `element`-rijen + relaties
  structureel op (residu-check na de run = 0).
