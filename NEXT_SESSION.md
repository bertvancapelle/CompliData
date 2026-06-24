# NEXT_SESSION.md — LIKARA V020

**Gegenereerd**: 2026-06-24 (sessie-afsluiting LI019)
**Build**: V019 → **V020**
**Migratie head**: `0041` (`0041_partij_aard_burger`) — geen schema-/migratiewijziging in LI019
**Tests**: frontend **595 groen (62 files)** + `vite build` ok; backend **864 passed / 2 skipped / 8 pre-existing
seed-afhankelijke failures** (identiek op schone HEAD, geen LI019-regressie). Zie `docs/TST-V020-Validatierapport.md`.

---

## Stand van zaken (V020) — Landschapskaart-filters/UI, auditlog-UI, leverancier via contract-keten

Deze sessie (LI019), puur frontend/afgeleid (engine onaangeroerd):

- **Sprint 1** — "Applicatie" → "Component" door de frontend; "Resultaten" → "Componenten" in de
  LK-zijbalk; type-indicator op graph-nodes.
- **Sprint 1b** — ZoekMultiSelect voor alle LK-filters (Type/Leverancier/Hosting/Lifecycle);
  leverancier-filter via de contract-keten; "× Wis"-knop per filter.
- **Sprint 1c** — filter-consistentie in alle modi; "Zonder [X]"-optie voor kenmerkloze nodes;
  ego-bevestigingsdialoog bij wegfilteren centrum.
- **Sprint 1d** — radiaal-layout voor alle views; auto-herpositionering + centrering;
  swimlane geïmplementeerd en uiteindelijk **geparkeerd** (toekomstige herwrite — ADR-034).
- **Sprint 1e** — auditlog-UI: "Wie"-fallback, systeem-actor labels, objectnaam, uitklapbare diff.
- **Sprint 1f** — leverancier via contract-keten op LK-nodes + LeverancierDetail componenten-sectie.
- **Bugfixes** — impactanalyse flow-koppelingen bidirectioneel; dubbelklik-hercentrering Ego;
  ringen in Impact-view.
- **Skills/docs** — complidata-frontend SKILL.md uitgebreid met de LI019-patronen; ADR-033
  (Impact-verkenner) vastgelegd; ADR-034 (swimlane-herwrite) als opvolgpunt.

---

## Top-5 prioriteiten volgende sessie (LI020)

1. **ADR-033 Impact-verkenner bouwen** — actieve set als selectie, drill-down, opgeslagen views.
2. **ADR-034 Swimlane herwrite** — pure HTML/CSS div-lanes + SVG-overlay voor edges (NIET Cytoscape
   compound-nodes); lane-drag, edges tussen lanes, nodes aanklikbaar.
3. **Codebase cleanup** — frontend 11 items + backend 28 items (zie cleanup-inventarisatie).
4. **ADR-029 Fase 5** — `gereedmeld_recht` per-type.
5. **ADR-030** — Contract-dekking per contract↔component band.

Volledige backlog: `docs/OPVOLGPUNTEN.md` (sectie "Stand V020 (LI019)").
