# SESSIE_BRIEFING.md — LIKARA V025

**Gegenereerd**: 2026-06-29

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V025 |
| Datum | June 2026 |
| Commit | 144ecd9 |
| Tests | backend 928 / frontend 745 groen (2 skipped) |
| TST-rapport | TST-V025-Validatierapport.md |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
144ecd9 test(landschapskaart): edge-only ring-toggle hertekent (regressie, LI037)
f8e735e fix(landschapskaart): eigenaar-edges verdwenen permanent — 'eigenaar' nu een echte ring (LI036)
0953857 feat(contract): ADR-030 per-band (component↔contract) dekking naast contract-brede dekking
d7052fa fix(login): generieke LIKARA-tagline op het splashscherm (LI035)
eb0a7ed fix(landschapskaart): detail-/legenda-paneel springt niet meer bij eerste sleep-beweging (LI034)
```

---

## Prioriteiten volgende sessie

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


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — LIKARA V025"
4. Wacht op START: [naam] van Bert
