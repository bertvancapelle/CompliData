# SESSIESTART — LIKARA V025

**Datum**: 2026-06-29
**Platform**: LIKARA — een product van G. van Capelle Beheer B.V.

---

## Instructie voor CC bij sessiestart

1. Lees dit document volledig
2. Voer de sessiestart uit conform CLAUDE.md:
   - Controleer of .claude/skills/likara/ bestaat
   - Zo ja: normale modus — lees alle likara-skills + engineering/security
   - Zo nee: bootstrap-modus — lees alleen engineering/security
3. Lees SESSIE_BRIEFING.md voor de actuele projectstatus
4. Bevestig: "Sessiestart compleet — LIKARA V025 — [N] skills geladen"
5. Wacht op START: [naam] van Bert

---

## Interactieregel (VERPLICHT — niet-onderhandelbaar)

Geldt voor zowel CC als claude.ai, in elke sessie:

- Stel vragen ALTIJD één voor één. Stel nooit meerdere vragen tegelijk.
  Wacht op het antwoord van Bert voordat je een volgende vraag stelt.
- Geef adviezen ALTIJD één voor één. Geef nooit meerdere adviezen tegelijk.
  Wacht op de reactie van Bert voordat je een volgend advies geeft.

Deze regel is niet-onderhandelbaar en overschrijft elke neiging om
meerdere vragen of adviezen te bundelen.

---

## Opdrachtformaat CC-opdrachten (VERPLICHT — standaardwerkwijze)

claude.ai levert elke CC-opdracht ALTIJD aan als een .md-bestand
(downloadbaar), nooit als een los codeblok in de chat. Bert gebruikt dat
.md-bestand in CC. Deze afspraak geldt in elke sessie.

---

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

