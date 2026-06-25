# TST-V022-Validatierapport

**Build**: V022
**Datum**: 2026-06-25
**Sessie**: LI021 (test-hygiëne `finally`-fix; seed-verrijking infra/samenstelling/scope-gaten; Landschapskaart-vertrekpunt **fase A** — set-scoped subgraaf-endpoint + leverancier-filter + eigenaar-edge)
**Migratie head**: `0042` (`0042_adr033_opgeslagen_view`) — **geen** nieuwe schema-/migratiewijziging in LI021 (test-hygiëne = test-only; seed-verrijking = data-only; fase A = additieve read-only projecties/filter)

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `py_compile` op alle Python (excl. node_modules/.git/__pycache__) | **Geslaagd** — 0 syntaxfouten |
| 2 — Tests | `pytest backend/tests modules -q` | **896 passed, 2 skipped, 8 failed** — alle 8 zijn **pre-existing live-DB-tests** (seed-drift, zie onder); **+6 nieuwe groen** t.o.v. V021 (fase A-tests) |
| 3 — Database-integriteit | migratie-head / branches | **Geslaagd** — 1 head (`0042_adr033_opgeslagen_view`), 0 branches. Geen schema-/migratiewijziging in LI021 |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/ + frontend/src/ + modules/ | **Geslaagd** — 0 code-hits (alleen historische CompliMan-context in `docs/adr/ADR-012`, geen code/output) |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` (`npm test`) | **Geslaagd** — **654 passed (62 files)** |
| `vite build` | **Geslaagd** — 0 fouten (alleen chunk-size-waarschuwing, geen error) |
| `npm run test:css-build` | **Geslaagd** — 6/6 kritische interactie-klassen aanwezig |

## Aantal kritieken

**0.** (Geen nieuwe kritieken; geen regressies door LI021. Alle fase A-backendwerk is additieve
read-projectie/afgeleide filter met dubbele engine-borging.)

## LI021-opleveringen (geland)

| Commit | Inhoud |
|---|---|
| `0c4371b` | **Test-hygiëne**: twee live-DB-tests zelf-opruimend via `finally` (cleanup draait ook bij falen → geen residu-lek meer; de vervuilings-cirkel gebroken) |
| `ae905c1` | **Seed-verrijking** `_seed_bvowb_scenario` (data-only, idempotent): infrastructuur (technology-laag) + draait-op-relaties; component-samenstelling (Burgerzaken-suite); bewuste scope-gaten (Archiefbeheer zonder eigenaar; Klantportaal uitsluitend organisatieloos gebruikt) |
| `fec08d5` | **Kaart-vertrekpunt fase A**: POST `/landschapskaart/subgraaf` (set-scoped, S+1-hop; `component_ids=None` = volledige graaf voor back-compat); leverancier-filter op `/componenten` (afgeleide EXISTS, beide paden); eigenaar-edge "is eigendom van" (context, **niet** in `IMPACT_RINGEN`) |

## Pre-existing backend-failures (8) — seed-drift, niet-blokkerend, opgelost door LI022

Dezelfde 8 als V021 (architectuur_f2, audit_capture, 4× component_fase_b_cd052, lifecycle_pertype,
vraagbeheer). **Niet** door LI021 veroorzaakt. De LI020/LI021 `finally`-hygiëne (commit `0c4371b`)
brak de residu-cirkel (een falende test lekt niet meer), maar de 8 blijven rood door een **dieper
liggende seed-drift**: de tests asserteren op rijen die het canonieke `_seed_bvowb_scenario` níét
(meer) maakt — o.a. `GeoWorks Licentieovereenkomst`, `Oracle FIN-DB` (uit dode seed-paden) en 3
`client_software`-checklistvragen (0 in de huidige DB).

**Oplossing = LI022 stap 1** (eerste actie volgende sessie): `docker compose down -v` → reseed
(**handmatige dev-seed!**) + de stale tests herijken op `_seed_bvowb_scenario`. **Niet** als
opgelost gemarkeerd — pas na groen in CC's omgeving.

## Conclusie

V022 is groen: backend 896 passed (+6 nieuw), frontend 654 passed, py_compile 0, 1 migratie-head,
0 code-conventieschendingen, 0 kritieken. De 8 pre-existing live-DB-failures zijn bekend (seed-drift)
en staan als eerste actie voor LI022 gepland.
