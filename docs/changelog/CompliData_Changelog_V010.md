# CompliData Changelog V010

**Datum**: 2026-06-15
**Sessie**: DC009
**Migratieketen**: t/m `0021`
**Tests**: 692 backend + 258 frontend groen (1 pre-existing, omgevingsgebonden env-test `test_auth_pkce`)
**Kritieke bevindingen**: 0
**Invariant geborgd**: score blijft de enige lifecycle-driver — engine onaangeroerd in alle slices.

## Geland deze sessie (ADR-023 voortzetting)

| Commit | Onderwerp |
|---|---|
| `a20c74e` | **ADR-023 Fase C** — technologielaag: laag-filter/-labels (read-side) + draait-op-aanmaak herbedraad naar de `/relaties`-API (cutover-residu opgeruimd) |
| `e683976` | **ADR-023 Fase D** — leverancier-onderscheid (UI/label) + ArchiMate-laag-borging (vaste element-typing + dekkingstest) |
| `4a20572` | **ADR-023 Fase E (E1)** — Plateau (element-subtype, FORCE RLS) + lidmaatschap (aggregation) met dispositie + contractuele bevestiging; nieuwe relatie-kenmerk-catalogus (`relatiekenmerk_optie`) |
| `21597ef` | **Consistentie-opruim** — `relatie_rol` verhuisd van ContractConfig naar de relatie-kenmerk-catalogus (functioneel ongewijzigd; `/contracten/opties` componeert) |
| `8adb32e` | **ADR-023 Fase E (E2)** — Work Package (element-subtype) + hiërarchie (composiet self-FK RESTRICT); cycluspreventie (servicelaag) + verwijdergedrag (409 `HEEFT_SUBPAKKETTEN`) |
| `2dc38aa` | **ADR-023 Fase E (E3)** — Deliverable (element-subtype) + realisatieketen work_package → deliverable → plateau via `realization` (facade, type-validatie, optioneel) |

## Migraties

`0018_adr023_plateau` · `0019_relrol_naar_relkenmerk` · `0020_adr023_workpackage` · `0021_adr023_deliverable`
— alle additief, element-subtype-patroon (shared-PK composiet-FK → `element`, FORCE RLS). Geen
datamigratie van bestaande data; ID's ≤32 tekens.

## RBAC / audit

Nieuwe permissie-entiteiten `PLATEAU` / `WORK_PACKAGE` / `DELIVERABLE` (`_INHOUD`-patroon); audit-allowlist
uitgebreid met `plateau`/`work_package`/`deliverable`/`relatiekenmerk_optie`. Relatie-koppelingen
(aggregation/realization) lopen via het bestaande `relatie`-audit-spoor.

## Skill-updates (DC009)

`complidata-db`, `complidata-backend`, `complidata-tests` bijgewerkt naar V010 met vier canonieke
patronen: (1) gate-per-schema-slice vs. doorloop-bij-licht-additief; (2) engine-onaangeroerd via dubbele
regressie-borging (offline import-afwezigheid + live geen-profiel); (3) element-subtype-bouwrecept
(shared-PK/FORCE RLS/composiet-FK/CASCADE; self-FK+RESTRICT bij hiërarchie); (4) facade-over-Relatie-
conventie voor nieuwe verbanden (bestaand relatietype, type-validatie per richting, geen nieuw type/FK
tenzij vaste ariteit). Dode `KoppelingConflict`-referentie in de backend-skill rechtgezet.

## Resteert

ADR-023 **Fase E — E4 (Gap + readiness-rollup)** als afsluitende migratielaag-slice; daarna **Fase F**
(gelaagde lees-API/views + E-8 checklist-consistentiecheck + RBAC/audit-afronding). Zie `OPVOLGPUNTEN.md`.
