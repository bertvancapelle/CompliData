# LIKARA — Next Session (LI025)

## Top-5 prioriteiten

1. **ADR-035 Slice 3** — Registratie onvolledig (score onder configureerbare drempelwaarde).
   Vereist platform-instelling (tenant-breed, default 80%). Aparte mini-slice.

2. **Modus ego→impact ontkoppelen van set-grootte** — automatische modus-wissel bij
   2+ set-leden voelt abrupt. Modus wordt expliciete gebruikerskeuze (tabs);
   ADR-033-revisie nodig.

3. **GebruikersgroepDetail — standalone pagina** — ontbreekt; gebruikersgroepen
   leven nu als sectie in ComponentDetail. Badge + signalering wachten hierop.

4. **BlokkadeDetail — standalone pagina** — ontbreekt; blokkades hebben alleen
   BlokkadeOverzichtView (lijst). Badge + signalering wachten hierop.

5. **Zoekbalk contextlabel** — "Component toevoegen aan beeld" boven de zoekbalk
   in kaart-modus (klein, cosmetic, 1 regel tekst).

## Openstaande punten (volledig)

### ADR-035 Signalering
- Slice 3: "Registratie onvolledig" (configureerbare score-drempelwaarde) — uitgesteld
- blokkade_zonder_eigenaar — structureel onmogelijk (roltoewijzing verwijst niet naar
  blokkade, blokkade is geen element-subtype); vereist schema-/semantiekherziening
- badges op GebruikersgroepDetail/BlokkadeDetail — uitgesteld tot detail-pagina's bestaan

### ADR-030
- Signaaltype "component zonder per-band dekking" als toekomstig ADR-035-signaaltype — genoteerd

### Landschapskaart
- Modus ego→impact ontkoppelen van set-grootte (ADR-033-revisie)
- Scope-balk gedrag in subgraaf-modus (bewust uitgesteld)
- Swimlane implementatie (ADR-034, geparkeerd)
- Saved views als permanente hoofdingang (Fase D)

### Platform
- GebruikersgroepDetail standalone pagina
- BlokkadeDetail standalone pagina
- fcose TOEGESTANE_ELEMENTEN uitbreiding (ADR-026-amendement, optioneel)

### Cosmetic/klein
- Zoekbalk contextlabel "Component toevoegen aan beeld" in kaart-modus

### Strategisch (parked)
- Export/import/rapportage — scope en fasering apart te bepalen
