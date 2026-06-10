# ADR-019 — Configureerbare antwoordopties per checklistvraag (additioneel veld, score behouden)

**Status**: Aanvaard (CD025)
**Datum**: juni 2026
**Context-ADR's**: ADR-009 (checklist-/score-datamodel), ADR-013 (lifecycle-herberekening),
ADR-016 (blokkade `opgelost` afgeleid), ADR-012 (tweelaags rollenmodel platform/tenant).

## Context

De 89 checklistvragen (referentiedata, `CHECKLIST_VRAGEN` → `checklistvraag`, platform-breed)
gebruiken allemaal dezelfde score-enum `ja` / `deels` / `nee` / `nvt` op `Checklistscore.score`.
Bij inspectie blijkt een groot deel van de vragen feitelijk **keuze-, tekst- of getalvraag**
(bv. 1.3 "eigenaar — BWB / Tiel / gedeeld", 2.1 "hostingmodel: SaaS / on-premise / IaaS / PaaS /
hybride", 3.2 "aantal actieve gebruikers", 4.1 "type data — combinatie"). Voor die vragen is
`ja/deels/nee/nvt` semantisch geen passend antwoord.

De wens: als beheerder per vraag de mogelijke antwoorden kunnen configureren, passend bij de vraag.

Een eerder voorstel (de score-enum vervangen door vrij-configureerbare opties met een per-optie
`blokkerend`-vlag) is **verworpen**: dat raakt de net-gevalideerde lifecycle-/blokkade-engine
(ADR-013/016) en de bestaande scores, met migratie- en regressierisico op logica die nu groen is
(462 backend / 127 frontend tests).

## Besluit

1. **De bestaande `score`-enum blijft per vraag staan en behoudt zijn functie en scoring**,
   voortaan expliciet als het **oordeel "is deze vraag afgehandeld / voldoet het?"**. De
   lifecycle-/blokkade-engine blijft **byte-identiek**: `nee`/`deels` → blokkade, alles gescoord
   zonder open blokkade → migratieklaar. Geen migratie van bestaande scores, geen generalisatie
   van de engine.

2. **Additioneel, alleen waar van toepassing, een configureerbaar gestructureerd antwoordveld**
   dat de feitelijke inhoud vangt. Per vraag een **antwoordtype**:
   - `geen` (default — alleen de score, zoals nu),
   - `enkelvoudige_keuze` (bv. 1.3, 2.1),
   - `meerkeuze` (bv. 4.1),
   - `vrije_tekst` (bv. 1.1 "naam"),
   - `getal` (bv. 3.2, 4.2).
   Voor de keuze-types beheert de beheerder een **geordende optielijst** per vraag.

3. **Het antwoordveld voedt de engine NIET.** Alleen `score` bepaalt blokkade/lifecycle. Het
   antwoordveld is puur registratie/inventarisatie. Daardoor is deze wijziging **additief**:
   een nieuw *nullable* antwoordveld op `Checklistscore` plus een nieuwe optie-configuratie als
   referentiedata — **geen wijziging aan bestaande tabellen of logica**.

4. **Drie lagen met onderscheiden rollen**, naast elkaar op de checklistregel:
   - `score` = oordeel/afgehandeld (voedt de engine);
   - het nieuwe antwoordveld = de **gevalideerde feitelijke waarde** (keuze/tekst/getal);
   - `bevinding` / `eigenaar` / `actie` (CD025) = vrije onderbouwing / verantwoordelijke / actie.
   Het antwoordveld is dus iets ánders dan `bevinding`: `bevinding` blijft vrije toelichting.

5. **Validatie bij opslaan**: het antwoordveld wordt backend-side gevalideerd tegen het
   geconfigureerde type en (voor keuze-types) de toegestane opties van die vraag.

6. **Beheerder-UI** om per vraag het antwoordtype + de opties te beheren. De checklist-uitklaprij
   (CD025) toont het antwoordveld waar geconfigureerd, naast de bestaande score-dropdown.

7. **UX**: de kolom "Score" wordt hernoemd naar **"Afgehandeld"** (of "Beoordeling") om verwarring
   met het nieuwe antwoordveld te voorkomen.

8. **De classificatie van de 89 vragen** (welke een extra veld krijgen, welk type, welke opties)
   levert de **default-configuratie** die mee wordt geseed. Vragen waar `ja/nee` volstaat houden
   antwoordtype `geen`.

9. **Reikwijdte: platform-breed (besloten, OP-A).** De antwoordtype-/optie-configuratie is
   platform-brede referentiedata bij de vraag, beheerd door de **platform-beheerder** (ADR-012,
   `cd_platform`) — niet per tenant. **Integriteitsregel:** optie-id's zijn stabiel en worden
   nooit hard verwijderd of hernummerd zodra een optie in gebruik kan zijn; bewerken =
   **soft-deactiveren** + een nieuwe optie toevoegen. Zo blijven historische tenant-antwoorden
   resolvebaar en raken ze niet stil verweesd. (Raakt OP-B: het antwoord verwijst naar een
   stabiel optie-id.)

10. **Opslag van het antwoord (besloten, OP-B).** Een **relationele optie-catalogus** als
    referentiedata (per vraag: stabiel optie-id, `actief`, label, volgorde) — de plek waar de
    soft-deactivate-regel uit Besluit 9 leeft. Het antwoord zelf staat in één nullable
    `antwoord_waarde` (**jsonb**) op `Checklistscore`: een optie-id (enkelvoudige keuze), een
    array van optie-id's (meerkeuze), of de vrije tekst-/getalwaarde. **Validatie bij opslaan:**
    de gekozen optie moet `actief` zijn en bij de vraag horen; bij uitlezen resolvet elk id (ook
    gedeactiveerde) via de catalogus. Geen database-FK nodig — het optie-id is stabiel en wordt
    nooit hard verwijderd.

11. **Antwoordveld en score ontgekoppeld (besloten, OP-C).** Score en `antwoord_waarde` zijn
    inhoudelijk onafhankelijk; het invullen van het ene verplicht het andere niet, en het
    antwoordveld wijzigt de score-afgeleide lifecycle/blokkade nooit. De enige afhankelijkheid is
    technisch en bestaat al: het veld leeft op `Checklistscore`, dus er moet eerst een score-rij
    zijn ("disabled-tot-gescoord", net als CD025-`bevinding`/`eigenaar`/`actie`).

12. **Optiesets vs. bestaande model-enums (besloten, CD025).** Waar een vraag *exact* hetzelfde
    domein beschrijft als een bestaande `Applicatie`-enum, wordt de optieset **afgeleid van die
    enum (single source)** en in de beheerder-UI **read-only** getoond (alleen het label is
    aanpasbaar; de enum-waarde is het stabiele optie-id) — zo is drift onmogelijk. Concreet:
    **2.1 hostingmodel ← `HostingModel`** (alle 7 waarden, incl. `private_cloud` en `onbekend`),
    **12.1 migratiecomplexiteit ← `NiveauEnum`** (Laag/Midden/Hoog). Waar de framing aantoonbaar
    anders is, blijft de optieset **vrij configureerbaar en onafhankelijk**: bv. **11.1
    ontvlechtingsscenario** (Overdracht Tiel / Overname BWB / Tijdelijk gedeeld / Beëindiging) ≠
    `Migratiepad`-techniek; 11.1 (scenario) en 11.3 (technische methode) zijn twee aparte assen.

## Gevolgen

- De gevalideerde engine en alle bestaande scores blijven ongemoeid; nul regressierisico op de
  blokkade-/lifecycle-logica.
- Het antwoordveld leeft op `Checklistscore`. Net als `bevinding`/`eigenaar`/`actie` (CD025) vereist
  het daarom dat de vraag eerst gescoord is (een `Checklistscore`-rij bestaat) — de bestaande
  "disabled-tot-gescoord"-UX geldt ook hier.
- Rapportage wordt rijker: de feitelijke antwoorden zijn gestructureerd en bevraagbaar i.p.v.
  verstopt in vrije tekst.

## Beslissingen (alle besloten — CD025)

**OP-A · Reikwijdte van de configuratie — BESLOTEN.** Platform-breed, beheerd door de
platform-beheerder, met stabiele en alleen soft-deactiveerbare optie-id's. Zie Besluit 9.

**OP-B · Opslag van het antwoord — BESLOTEN.** Relationele optie-catalogus + één jsonb
`antwoord_waarde` op `Checklistscore`, app-side gevalideerd. Zie Besluit 10.

**OP-C · Koppeling antwoordveld ↔ score — BESLOTEN.** Ontkoppeld. Zie Besluit 11.

## Implementatie (CD027–CD035, fasen 2A–2E)

- **2A (CD027)** — datamodel + migratie `0003_antwoordconfig` + seed (`AntwoordType`, kolom
  `antwoordtype` op `ChecklistVraag`, tabel `checklistvraag_optie`, jsonb `antwoord_waarde` op
  `Checklistscore`; 27 getypeerde vragen / 96 opties; afgeleide sets 2.1/12.1).
- **2B (CD028)** — backend read/write + validatie (structureel in Pydantic → 422 native;
  semantisch tegen de catalogus → `OngeldigAntwoord` 422-envelope).
- **2C (CD029)** — scoring-UI: antwoordcontrole per type in de uitklaprij; kolom "Afgehandeld".
- **2D (CD031)** — platform-config-endpoints (`/platform/checklistconfig`) + RBAC
  (ADR-012 Addendum A); orphan-bescherming (type alleen vanuit `geen`), afgeleide sets read-only.
- **2E (CD032–CD034)** — `GET /auth/platform/me`, sessietype-bewuste SPA-auth + beheer-shell,
  beheer-UI `ChecklistConfigBeheer`.
- **Dev-seed (CD030)** — `antwoord_waarde` op de getypeerde rijen (256), 2.1 = werkelijk
  hostingmodel.
- **O2 (CD035)** — 7.5 BIO2 → BBN via expand/contract (seed + migratie `0004` soft-deactivate).

## Niet in scope

- Het **vervangen** van de score-enum of het **generaliseren** van de blokkade-engine (verworpen,
  zie Context).
- Per-tenant overrides van de configuratie (platform-breed).
- Apart `vrije_tekst`-antwoordveld: valt samen met `bevinding` (CD025) → die vragen houden `geen`.

## Alternatieven overwogen

- **Score-enum vervangen + per-optie `blokkerend`-vlag** (engine generaliseren): elegant in theorie,
  maar migratie-/regressierisico op de gevalideerde engine en bestaande scores. Verworpen.
- **Inventarisatie en gereedheidsoordeel ontkoppelen**, met iets ánders dat blokkade/migratieklaar
  bepaalt: de engine werkt en moet blijven; onnodig ingrijpend. Verworpen.
