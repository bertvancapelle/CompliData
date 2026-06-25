# TST-V021-Validatierapport

**Build**: V021
**Datum**: 2026-06-25
**Sessie**: LI020 (ADR-033 volledig; gebruikersbeheer-acties ADR-029 Fase 2b; Landschapskaart-reeks: vorm-per-type + uitklapbare legenda, toestand-geschiedenis + hang-fix + auto-centreren, selectie-highlight, organisatiestructuur-ring, organisatie-scopebalk slice 1+2)
**Migratie head**: `0042` (`0042_adr033_opgeslagen_view`) — geen nieuwe schema-/migratiewijziging in LI020 (kaart-projecties zijn read-only/afgeleid; gebruikersbeheer is Keycloak + read-verrijking)

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `py_compile` op alle Python (excl. node_modules/.git/__pycache__) | **Geslaagd** — 0 syntaxfouten (exit 0; alleen een SyntaxWarning in een overgenomen MS365-skill-script, geen error) |
| 2 — Tests | `pytest backend/tests modules -q` | **890 passed, 2 skipped, 8 failed** — alle 8 zijn **pre-existing live-DB-tests**; oorzaak deze sessie aangetoond: test-residu (zie onder) |
| 3 — Database-integriteit | migratie-head / branches | **Geslaagd** — 1 head (`0042_adr033_opgeslagen_view`), 0 branches. Geen schema-/migratiewijziging in LI020 |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/ + frontend/src/ + modules/ + docs/adr/ | **Geslaagd** — 0 hits |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` | **Geslaagd** — **654 passed (62 files)** |
| `vite build` | **Geslaagd** — 0 fouten (alleen chunk-size-waarschuwing, geen error) |
| `npm run test:css-build` | **Geslaagd** — 6/6 kritische interactie-klassen aanwezig |

## Aantal kritieken

**0.** (Geen nieuwe kritieken; geen regressies door LI020.)

## Pre-existing backend-failures (8) — oorzaak deze sessie aangetoond, niet-blokkerend

De 8 falers zijn **niet** door LI020 veroorzaakt (alle LI020-backendwerk is additieve read-projectie
met dubbele engine-borging). De **oorzaak is deze sessie getraceerd** (feitencheck artefact-herkomst):
twee live-DB-tests ruimen hun rijen **inline** op i.p.v. in `finally`, falen vóór dat punt en stapelen
**32 wees-componenten** (`CD052-db-*`, `AUDIT-SRV-*`) op die de lijst-/sort-asserts van ándere live-DB-
tests vervuilen → vicieuze cirkel. Dit verklaart óók de "reseed lost het op"-observatie.

**Structureel op te lossen door LI021-startpunt 1** (de twee tests zelf-opruimend maken via `finally`)
+ een schone reset (`docker compose down -v` → reseed). **Niet** als opgelost gemarkeerd — pas na die fix.

1. `test_architectuur_f2.py::test_architectuur_sortering_en_keyset_live`
2. `test_audit_capture_live.py::test_score_write_driver_plus_afgeleide_delen_correlatie`  ← lekt `AUDIT-SRV-*`
3. `test_component_fase_b_cd052.py::test_lijst_levert_besturingsvelden_en_statusfilter`
4. `test_component_fase_b_cd052.py::test_lijst_laag_filter_en_projectie`
5. `test_component_fase_b_cd052.py::test_structuur_overzicht_beide_richtingen`
6. `test_component_fase_b_cd052.py::test_component_contract_op_niet_applicatie_component`  ← lekt `CD052-db-*`
7. `test_lifecycle_pertype_adr022.py::test_pertype_scoping_negeert_ander_type`
8. `test_vraagbeheer_w1_fanout.py::test_vraag_toevoegen_en_deactiveren_fan_out`

## Geaccepteerde afwijkingen

- De 8 pre-existing live-DB-failures (hierboven) — bekende oorzaak, structurele fix gepland als eerste blok LI021.
