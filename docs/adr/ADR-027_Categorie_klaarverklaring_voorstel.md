# ADR-027 — Categorie-klaar-verklaring en voortgangsrapportage

**Status:** Voorstel (open subknopen nog te beslissen)
**Datum:** 2026-06-17
**Relatie:** Bouwt voort op ADR-022 (tenant-eigen checklist met categorieën) en ADR-024
(partijenregister + verantwoordelijkheidstoewijzing — nodig voor onderdeel 4). **Te plannen NÁ
ADR-024.**
**Invariant (ongewijzigd):** score blijft de enige lifecycle-driver — de engine wordt niet
geraakt. De categorie-klaar-verklaring is een **volledig gescheiden, niet-scorend mechanisme**:
het telt niet mee in de scoring, voedt de engine niet, en leidt niets af.

---

## Context / aanleiding

Bij een groot inventarisatietraject (de ontvlechting kent 250+ applicaties) verschuift de behoefte
van "kan ik dit invullen?" naar "waar moet ik zijn, en hoe sta ik ervoor?". Wat vandaag ontbreekt
is **voortgangsinzicht per checklist-categorie** — zowel per component als over het hele landschap.

Twee dingen die nu door elkaar dreigen te lopen, en die dit ADR juist uit elkaar trekt:

- **De checklist-score** is de motor van de lifecycle (concept → in inventarisatie → checklist
  compleet → …). Dat is een **machinale** maat: "hebben de vragen een waarde, en wat zegt de
  scoring". Engine-gedreven, bestaand, ongemoeid.
- **Of een categorie "af" is** is een **menselijk oordeel**. Bij grote aantallen is "alle vragen
  hebben een waarde" geen betrouwbare maat voor "klaar" — een verantwoordelijke moet expliciet
  kunnen verklaren: *"ik heb deze categorie beoordeeld en beschouw hem als afgehandeld."* Dat
  oordeel is juist wat je wilt sturen en rapporteren.

Daarnaast worden categorieën in de praktijk vaak door **bepaalde mensen of groepen** uitgevoerd
(de ene categorie ligt bij functioneel beheer, de andere bij security, een derde bij een
leverancier). Voortgang per categorie afgezet tegen wie verantwoordelijk is, levert dan
werkverdeling-/sturingsinzicht op.

Dit ADR voert daarom een expliciete, menselijke **categorie-klaar-verklaring** in, met
voortgangsrapportage op drie niveaus — strikt gescheiden van de score-engine.

---

## Besluit (kern)

1. **Categorie-klaar-verklaring (niet-scorend).** Per checklist-categorie op een component kan een
   verantwoordelijke de categorie expliciet **klaar verklaren**, met een **verplicht
   verklaring-veld** (wie/oordeel). Dit is een registratie, geen beoordelingsvraag: het telt niet
   mee in de score en voedt de engine niet.
2. **Voortgang per categorie op het component.** Voor één component in één oogopslag zien welke
   categorieën klaar verklaard zijn en welke nog openstaan (read-only afgeleid uit de verklaringen).
3. **Tenant-brede voortgangsrapportage per categorie.** Over alle applicaties heen: per categorie
   hoeveel componenten klaar verklaard zijn vs. nog open — stuurinformatie voor het hele traject.
4. **Werkverdeling-inzicht.** Voortgang per categorie afgezet tegen **wie/welke partij of groep
   verantwoordelijk** is per categorie. Leunt op de ADR-024 verantwoordelijkheidstoewijzing en komt
   daarom ná ADR-024.

### Kerninvariant (besloten)
De categorie-klaar-verklaring en de score-engine zijn **twee volledig gescheiden mechanismen**.
De klaar-verklaring is hetzelfde soort niet-scorende registratie als de **contractuele bevestiging
op plateau-lidmaatschap** (ADR-023 Fase E): puur registratief, het systeem leidt of berekent er
niets uit richting lifecycle/score. "Categorie klaar verklaard" en "checklist compleet"
(engine-status) zijn twee onafhankelijke assen die naast elkaar mogen bestaan en getoond worden,
maar elkaar niet aansturen.

---

## Model in detail

### De klaar-verklaring (registratie op component × categorie)
- Eenheid van registratie: de combinatie **(component, checklist-categorie)**. Per zo'n combinatie
  ten hoogste één levende klaar-verklaring.
- Inhoud (registratiegegevens, het systeem valideert/vergelijkt niets): **verklaard door**,
  **verklaard op**, en het **verplichte verklaring-veld** (oordeel/toelichting). Optioneel een
  status "klaar / (weer) open".
- **Niet als gewone checklistvraag.** Een klaar-verklaring als reguliere vraag zou hem de
  score-engine insleuren (vragen voeden de score). Daarom wordt hij gemodelleerd als een
  **aparte, niet-scorende registratie** — buiten de scorings-/lifecycle-paden, machine-geborgd
  (zie invarianten). Functioneel mag hij in de UI bovenaan elke categorie staan als verplichte
  aftekenhandeling; onderliggend is het geen scorende vraag.
- Tenant-scoped (RLS), conform de checklist-data uit ADR-022.

### Voortgang (read-only afgeleid)
- **Per component:** per categorie de status "klaar verklaard / nog open", plus een samenvatting
  ("X van Y categorieën klaar").
- **Tenant-breed:** per categorie de telling/verhouding klaar vs. open over alle (profiel-dragende)
  componenten — afgeleid uit de verklaringen, niets opgeslagen als tweede bron.
- De voortgang-as is gebaseerd op de **verklaringen**, niet op de scores. Een eventuele
  "vragen-beantwoord"-indicatie kan los read-only uit de engine-state komen, maar wordt niet met
  de verklaring-as vermengd.

### Werkverdeling (onderdeel 4, ná ADR-024)
- Koppel checklist-categorie aan de **verantwoordelijke partij/groep** via de ADR-024
  verantwoordelijkheidsrelatie (partij → object, met rol/categorie).
- Rapportage: voortgang per categorie afgezet tegen de verantwoordelijke — "categorie X loopt
  achter, en die ligt bij groep A".

### Waarom dit aansluit op bestaande patronen
- De klaar-verklaring hergebruikt het bewezen patroon van de **niet-scorende
  registratie-bevestiging** (plateau-lidmaatschap): registratie naast de engine, geen afleiding.
- De voortgangsweergave hergebruikt de bestaande **signalering-/status-/doorklik-primitieven**
  (status-indicator, lijstfilter, dashboard-telling met doorklik) waar zinvol — als read-only
  leeslaag.

---

## Invarianten

- **Engine onaangeroerd / score blijft enige lifecycle-driver.** De klaar-verklaring en de
  voortgangsrapportage voeden de engine niet en muteren geen lifecycle/score/blokkade. Dubbele
  regressie-borging per slice (offline import-afwezigheid + live geen-mutatie), zoals bij elke
  entiteit naast de engine.
- **Twee gescheiden assen.** "Categorie klaar verklaard" ≠ "checklist compleet" (engine). Ze worden
  nooit in één maat gemengd.
- **Voortgang is read-only afgeleid** uit de verklaringen; geen opgeslagen tweede bron.
- **Structureel boven conventioneel:** de niet-scorende aard van de verklaring wordt machinaal
  geborgd (de verklaring zit aantoonbaar buiten de scorings-/lifecycle-paden), niet alleen bedoeld.

---

## Gevolgen

- **Afhankelijkheid van ADR-024 voor onderdeel 4.** Onderdelen 1–3 (verklaring + voortgang per
  component + tenant-brede rapportage) kunnen zonder ADR-024; het werkverdeling-inzicht (4) komt
  erbij zodra het partijenregister + de verantwoordelijkheidstoewijzing er zijn. Natuurlijke
  fasering.
- **Raakt ADR-022.** De checklist-categorieën bestaan al; dit ADR hangt de verklaring en de
  voortgang aan die bestaande categorie-structuur.
- **RBAC/audit:** wie mag een categorie klaar verklaren en weer openen, en de verklaringen worden
  geauditeerd (append-only historie via de bestaande audit-trail). Nieuwe permissie-entiteit conform
  het bestaande patroon.
- **Bewust géén harde poort.** De klaar-verklaring blokkeert niets in de engine of de workflow; ze
  is sturings-/rapportage-informatie. Een categorie kan "nog open" zijn terwijl de scoring al
  "compleet" zegt, en omgekeerd — dat is geen inconsistentie maar twee verschillende assen.

---

## Open subknopen (te beslissen vóór de bouw — met voorlopige default)

1. **Modellering van de verklaring.** Aparte niet-scorende registratie-entiteit op
   (component, categorie) vs. een niet-scorend categorie-kenmerk. *Default: aparte niet-scorende
   registratie-entiteit (zoals de plateau-bevestiging), expliciet buiten de score-/lifecycle-paden.*
2. **Wie mag verklaren (RBAC).** Een rol-gebaseerde permissie, en/of gekoppeld aan de
   ADR-024-verantwoordelijke voor die categorie. *Default: rol-gebaseerde permissie; aansluiten op
   de ADR-024-verantwoordelijkheid waar beschikbaar — bevestigen.*
3. **Herroepbaarheid.** Mag een klaar verklaarde categorie weer geopend worden (status terug naar
   open)? *Default: ja, met audit-historie (aftekenen is herroepbaar; wie/wanneer geborgd in de
   audit-trail).*
4. **Voortgang-granulariteit.** Binaire as (klaar verklaard / niet) als kern. *Default: binair op de
   verklaring-as; een eventuele "deels beantwoord"-indicatie komt los read-only uit de engine-state
   en wordt niet met de verklaring-as gemengd.*
5. **Verplicht verklaring-veld — vorm.** Vrije tekst (oordeel/toelichting) als verplicht veld.
   *Default: verplichte vrije tekst; eventueel later een keuzelijst-dimensie via de
   relatiekenmerk-catalogus als de praktijk om standaardisatie vraagt.*
6. **Reikwijdte van "categorie".** De klaar-verklaring geldt voor de checklist-categorieën uit
   ADR-022 (tenant-eigen). *Default: per tenant-eigen categorie; geen platform-brede categorie-set
   opleggen.*
7. **Werkverdeling-rapportagevorm (onderdeel 4).** *Default: ná ADR-024 een kruisweergave
   categorie × verantwoordelijke partij/groep met voortgangstelling; vorm bevestigen wanneer
   ADR-024 er is.*

---

## Bouw-fasering (indicatief, ná besluitvorming en ná ADR-024)

1. **Klaar-verklaring registratie-model** (niet-scorend) — entiteit op (component, categorie) +
   verplicht verklaring-veld + RBAC + audit + engine-onaangeroerd dubbele borging. **Gate**
   (schema/RLS/RBAC/audit).
2. **Voortgang per categorie op het component** — read-only weergave (status per categorie +
   samenvatting). Licht/additief (read-side/frontend) → doorloop.
3. **Tenant-brede voortgangsrapportage** — read-only telling/verhouding per categorie over alle
   applicaties, met doorklik naar de betreffende componenten. Licht/additief → doorloop.
4. **Werkverdeling-inzicht** — koppeling aan de ADR-024-verantwoordelijkheid; voortgang per
   categorie × verantwoordelijke. Ná ADR-024; gate of doorloop afhankelijk van schema-impact.

Elke slice met engine-onaangeroerd-borging (offline import-afwezigheid + live geen-mutatie) en de
gangbare gate-discipline.
