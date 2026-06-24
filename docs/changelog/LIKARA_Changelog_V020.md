# LIKARA Changelog V020

**Datum**: 2026-06-24
**Sessie**: LI019

## Wijzigingen

### Sprint 1 — UI-hernoeming + type-indicator
- "Applicatie" → "Component" door de hele frontend; "Resultaten" → "Componenten" in de
  Landschapskaart-zijbalk; type-indicator op de graph-nodes.

### Sprint 1b — Landschapskaart-filters (ZoekMultiSelect)
- ZoekMultiSelect voor alle LK-filters (Type / Leverancier / Hosting / Lifecycle);
  leverancier-filter via de contract-keten; "× Wis"-knop per filter.

### Sprint 1c — Filter-consistentie
- Filters consistent in alle modi; "Zonder [X]"-optie voor kenmerkloze nodes;
  ego-bevestigingsdialoog bij het wegfilteren van het centrum-component.

### Sprint 1d — Layout
- Radiaal-layout voor alle views; auto-herpositionering + centrering na elke wijziging;
  swimlane geïmplementeerd en vervolgens geparkeerd (toekomstige herwrite — ADR-034).

### Sprint 1e — Auditlog UI
- "Wie"-fallback-keten, systeem-actor labels, objectnaam (entiteit_naam batch-resolver),
  en uitklapbare diff per rij in AuditTrailView.

### Sprint 1f — Leverancier via contract-keten
- `leverancier_id` op LK-nodes afgeleid via roltoewijzing (leidend) + contract-keten
  (component → association → contract.leverancier_id); LeverancierDetail (PartijDetail) met
  "Componenten"-sectie via `GET /partijen/{id}/componenten`.

### Bugfixes
- Impactanalyse: flow-koppelingen bidirectioneel meegenomen.
- Dubbelklik-hercentrering in de Ego-view.
- Ringen zichtbaar in de Impact-view.

### Skills / docs
- complidata-frontend SKILL.md uitgebreid met de LI019-patronen (ZoekMultiSelect, LK-filter-
  patronen, auto-herpositionering, getekendeNodes-regel, auditlog-UI, leverancier via
  contract-keten, swimlane-geparkeerd).
- ADR-033 (Impact-verkenner) vastgelegd; OPVOLGPUNTEN.md LI019-sectie; ADR-034 (swimlane-herwrite)
  als opvolgpunt.

### Engine-invariant
- Alle wijzigingen frontend/afgeleid; geen schema/migratie/engine-aanpassingen.
