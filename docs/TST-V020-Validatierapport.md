# TST-V020-Validatierapport

**Build**: V020
**Datum**: 2026-06-24
**Sessie**: LI019 (Landschapskaart-filters/UI, auditlog-UI, leverancier via contract-keten, radiaal-layout + swimlane geparkeerd)
**Migratie head**: `0041`

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `compileall` op backend/app, backend/tests, modules | **Geslaagd** — 0 syntaxfouten (exit 0) |
| 2 — Tests | `pytest backend/tests modules -q` | **864 passed, 2 skipped, 8 failed** — alle 8 zijn **pre-existing seed-afhankelijke live-tests**, niet door LI019 veroorzaakt (zie onder) |
| 3 — Database-integriteit | migratie-head / branches | **Geslaagd** — 1 head (`0041_partij_aard_burger`), 0 branches. Geen schema-/migratiewijziging in LI019 (alles frontend/afgeleid) |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/app + modules (`*.py`) | **Geslaagd** — 0 hits |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` | **Geslaagd** — **595 passed (62 files)** |
| `vite build` | **Geslaagd** — 0 fouten (alleen chunk-size-waarschuwing, geen error) |

## Aantal kritieken

**0.** (Geen nieuwe kritieken; geen regressies door LI019.)

## Pre-existing backend-failures (8) — gedocumenteerd, niet-blokkerend

Deze 8 falen seed-/data-afhankelijk en zijn aantoonbaar onafhankelijk van de LI019-wijzigingen
(LI019 is puur frontend/afgeleid; geen backend-, schema- of seed-wijziging). Opvolgpunt: skip-robuust
maken (zie OPVOLGPUNTEN.md "Stand V020").

1. `test_architectuur_f2.py::test_architectuur_sortering_en_keyset_live`
2. `test_audit_capture_live.py::test_score_write_driver_plus_afgeleide_delen_correlatie`
3. `test_component_fase_b_cd052.py::test_lijst_levert_besturingsvelden_en_statusfilter`
4. `test_component_fase_b_cd052.py::test_lijst_laag_filter_en_projectie`
5. `test_component_fase_b_cd052.py::test_structuur_overzicht_beide_richtingen`
6. `test_component_fase_b_cd052.py::test_component_contract_op_niet_applicatie_component`
7. `test_lifecycle_pertype_adr022.py::test_pertype_scoping_negeert_ander_type`
8. `test_vraagbeheer_w1_fanout.py::test_vraag_toevoegen_en_deactiveren_fan_out`

## Invariant-borging (LI019, geverifieerd)

- Engine onaangeroerd; geen schema/migratie/seed-wijziging — alle LI019-werk frontend/afgeleid.
- Geen `localStorage`-tokens, geen hardcoded tenant/platform/operator-referenties toegevoegd.
- RLS-/tenant-isolatiepatronen ongemoeid.

## Eindoordeel

**Akkoord voor V020.** Frontend volledig groen (595); backend 864 groen met 8 gedocumenteerde
pre-existing failures (0 nieuwe). 0 kritieken.
