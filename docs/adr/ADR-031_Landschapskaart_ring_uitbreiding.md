# ADR-031 — Landschapskaart: ring-uitbreiding (Gebruikers + Rollen) en edge-interactie

**Status:** Besloten
**Datum:** 2026-06-23
**Relatie:** Bouwt voort op de bestaande Landschapskaart (ego-view, Cytoscape.js) en ADR-024
(roltoewijzing). Leest bestaande data; engine onaangeroerd.
**Invariant:** score blijft de enige lifecycle-driver — puur read-only.

## Context
De Landschapskaart heeft vier ringen (Applicaties, Beheerorganisatie, Contracten, Infrastructuur).
Drie gaten in de gebruikerservaring:
1. Klikken op een lijn geeft geen popup — roltoewijzingsdetails (rol, partij, contract) zijn onzichtbaar.
2. Gebruikersgroepen ontbreken volledig als ring — "wie gebruikt dit?" is niet zichtbaar.
3. Granulariteit is alles-of-niets — geen instelling per ring.

## Besluiten

1. **Twee nieuwe ringen naast de bestaande vier:**
   - **Gebruikers** — gebruikersgroepen als nodes met ledenaantal-badge, gekoppeld via serving-relatie.
   - **Rollen** — roltoewijzingen als edges met rol-label zichtbaar op de lijn (geen klik nodig voor de naam).

2. **"Beheerorganisatie" → "Rollen & beheer"** — partij-nodes blijven; rol-labels komen op de verbindingslijnen.

3. **Edge-popup (geldt voor alle rings)** — klikken op een lijn opent een popup met:
   rol_label, partij-naam en richting — direct uit edge-data, geen extra API-call.

4. **Sub-granulariteit in "Gebruikers"-ring** — toggle "Groepeer per organisatie":
   - Uit (default): individuele gebruikersgroepen als nodes.
   - Aan: aggregeer per organisatie-partij met gesommeerd ledenaantal.

5. **Ringen zijn altijd onafhankelijk aan/uit te zetten** — granulariteit per ring, niet globaal.
   Meer ringen aan = meer context; gebruiker bepaalt de drukte zelf.

## Invarianten
- Engine onaangeroerd / score blijft enige driver.
- Geen nieuwe relaties of afgeleide data — toont alleen expliciet geregistreerde relaties.
- Dubbele engine-borging per slice (offline import-afwezigheid + live geen-profiel-mutatie).

## Bouw-fasering
1. Backend: ego-graph endpoint verrijken met gebruikersgroepen + ledentelling + roltoewijzing-details op edges.
2. Frontend: nieuwe ring-checkboxes + gebruikersgroep-nodes + edge-popup + rol-labels op edges + sub-granulariteit toggle.

Elke slice read-only met engine-onaangeroerd-borging. Geen schema/migratie verwacht.
