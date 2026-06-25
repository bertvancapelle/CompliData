# LIKARA Changelog V021

**Datum**: 2026-06-25
**Sessie**: LI020

## Wijzigingen

### ADR-033 — Impact-verkenner + opgeslagen views (volledig)
- Adaptieve Landschapskaart: één graph-pipeline voor alle modi (leeg → geheel, 1 → ego,
  ≥2 → Impact-verkenner); geen view-tabs. Drill-down op het canvas.
- Samenstelling-edge ("onderdeel van") als component↔component-aggregatie op de kaart.
- Opgeslagen & deelbare views: eigen entiteit (`impact_view` + junction) + rechten (IMPACT_VIEW)
  + API + voorkant + startscherm bij ≥1 opgeslagen view.

### ADR-029 Fase 2b — gebruikersbeheer-acties (achter + voorkant)
- Vier acties op een bestaande gebruiker (alleen tenant-Beheerder): wachtwoord opnieuw
  instellen (eenmalig getoond), rol wijzigen (vier rollen), in-/uitschakelen (directe
  Keycloak-sessie-afkap), gegevens corrigeren (persoon-partij + Keycloak).
- Self-lockout-guards (niet je eigen account uitschakelen/de-beheerrollen; niet de laatste
  beheerder); expliciete audit per actie (wachtwoord nergens gelogd); lijst verrijkt met rol + status.
- Beheer-paneel per rij met begrijpelijke foutmapping (403/404/409/422/503).

### Landschapskaart-reeks (frontend, engine onaangeroerd)
- **Selectie-highlight**: enkelklik = inspecteren (detail + alleen incidente lijnen oranje via
  runtime `hl-node`/`hl-edge`); dubbelklik = dieper (impact-drill / ego-hercentreren). Lijnen standaard neutraal.
- **Organisatiestructuur-ring**: "hoort bij" (persoon-met-rol → afdeling → organisatie, van onderaf;
  afdeling-NULL → direct persoon→organisatie). Context — standaard uit, buiten `IMPACT_RINGEN`.
- **Toestand-geschiedenis** (terug/vooruit, browser-model) + **hang-fix** (herstel zonder geforceerde
  geanimeerde relayout: inhoud-vergelijking + `animate:false`; centreren via layout-stop; history
  begrensd ~50 + `shallowRef`/bevroren snapshots; filter-watch afgeschermd). Auto-centreren erin opgegaan.
- **Vorm-per-type** via één gedeelde bron (`_vormVoorType` → `_nodeData.shape`); kleur = status, vorm =
  type; tekstkleur altijd via luminantie; type-label voor alle typen; **uitklapbare legenda** (Vorm/Kleur).
- **Organisatie-scopebalk**: slice 1 (backend read-projectie — `eigenaar_organisatie_id` +
  `gebruikt_door_organisaties` + org-loos-flag, afgeleid uit bestaande relaties) + slice 2 (vaste balk:
  organisatie-checkboxes + Biedt-aan/Gebruikt-schakelaar; gaten eerlijk getoond; in de geschiedenis).

### ADR's
- **ADR-034 (swimlane-herwrite)** vastgelegd als Voorstel.

### Skills / docs
- complidata-frontend / -tests / -backend bijgewerkt met de LI020-patronen; CONTRIBUTING.md commit-discipline (één-slice-één-commit).

## Bekend / opvolg
- 8 pre-existing live-DB-failures: oorzaak getraceerd (test-residu — niet-zelf-opruimende live-DB-tests).
  Structureel opgelost als eerste blok LI021 (zie `docs/TST-V021-Validatierapport.md` + OPVOLGPUNTEN.md).
- Geen schema-/migratiewijziging (head blijft `0042`).
