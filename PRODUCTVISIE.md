# LIKARA — Productvisie

**Logische ICT Kaart Afhankelijkheden Relaties Analyse**

---

## Het probleem

ICT-landschappen van organisaties zijn gefragmenteerd gedocumenteerd — of helemaal niet. Applicaties, infrastructuur, contracten en verantwoordelijkheden leven in losse spreadsheets, mailwisselingen en hoofden van mensen. Het gevolg: beslissingen over uitfasering, migratie en contractverlenging worden genomen zonder volledig afhankelijkheidsinzicht. Niemand heeft een betrouwbaar antwoord op de vraag: *wat raakt het als dit component verdwijnt?*

LIKARA vult dit gat.

---

## Wat LIKARA is

LIKARA is een registratie- en inzichtplatform voor het ICT-landschap van een organisatie. Het centrale principe: alles wat relevant is om een ICT-component te begrijpen staat op één plek — en is verbonden met alles wat ertoe doet.

LIKARA maakt het mogelijk om op eenvoudige wijze de volledige context van een component vast te leggen en de onderlinge relaties te leggen. Het resultaat is een logisch, volledig en navigeerbaar model van het hele ICT-landschap — geen statische documentatie, maar een levend overzicht dat meegroeit met de organisatie.

---

## Voor wie

LIKARA is gebouwd voor gemeenten en overheidsorganisaties die grip willen krijgen op hun ICT-landschap, met name in de context van transities, ontvlechtingen en migratietrajecten.

Binnen een organisatie bedient LIKARA meerdere rollen:

- **De registrerende beheerder** — legt componenten, relaties, contracten en eigenaarschap vast en houdt de registratie actueel.
- **De architect** — analyseert afhankelijkheden, beoordeelt landschapssamenstellingen en bereidt architectuurbesluiten voor.
- **De projectleider / transitieverantwoordelijke** — bewaakt de gereedheid van componenten voor migratie en ziet waar gaten zitten.
- **De manager / bestuurder** — krijgt inzicht in het landschap in begrijpelijke taal, zonder architectuurtechnisch jargon.

---

## Wat je vastlegt

Per component leg je alles vast wat nodig is om het te begrijpen en te besturen:

- **De component zelf** — applicatie, infrastructuur, datatype, platform of ander elementtype, inclusief laag en architectuurpositie.
- **Koppelingen** — welke componenten wisselen data uit, welke zijn afhankelijk van elkaar, welke draaien op welke infrastructuur.
- **Gebruikersgroepen** — wie binnen de organisatie gebruikt het, vanuit welke afdeling of organisatie-eenheid.
- **Contracten en leveranciers** — welke contracten gelden, wie levert de dienst, wat zijn de looptijden en voorwaarden.
- **Eigenaarschap en verantwoordelijkheid** — wie is functioneel, technisch en contractueel verantwoordelijk; rollen zijn expliciet toewijsbaar aan personen, afdelingen en externe partijen.
- **Lifecycle-status** — hoe volledig is de registratie, welke vragen zijn beantwoord, is het component klaar voor een besluit.

---

## Wat LIKARA oplevert

**Landschapsinzicht.** De Landschapskaart maakt het model visueel en interactief. Je kiest een startpunt — een applicatie, een leverancier, een contract, een gebruikersgroep — en ziet direct de directe omgeving. Via expliciete navigatie verdiep je stap voor stap. Elke plaat blijft leesbaar omdat je nooit het volledige landschap in één keer toont, maar altijd vanuit een gekozen focus werkt.

**Impactinzicht.** Welke componenten, gebruikers, contracten en verantwoordelijken raakt een transitie? LIKARA maakt dit antwoord beschikbaar vóórdat een besluit wordt genomen — niet achteraf.

**Governancebeheer.** LIKARA is niet alleen registratie maar ook borging. De lifecycle-score per component meet de volledigheid van de registratie. Klaarverklaringen leggen vast dat een component gereed is voor een volgende fase. Blokkades signaleren wat een voortgang in de weg staat. Signalering maakt registratiegaten actief zichtbaar: een component zonder eigenaar, een contract zonder leverancier, een gebruikersgroep zonder organisatie.

De kaart is zo goed als de registratie — LIKARA stimuleert volledigheid actief.

---

## Architectuurgrondslag

LIKARA is opgebouwd op een ArchiMate-aligned elementmodel (curated core subset). Elk componenttype, elke relatie en elk element heeft een expliciete architectuurpositie (laag, aspect, elementtype). Dit biedt een professionele, gestandaardiseerde basis die:

- consistentie borgt over de gehele registratie,
- interoperabiliteit met EA-tooling mogelijk maakt,
- en uitbreidbaar is zonder de structurele integriteit aan te tasten.

Relaties worden altijd expliciet gelegd door gebruikers — het systeem leidt nooit relaties af.

---

## Generiek multi-tenant platform

LIKARA is een generiek platform, inzetbaar voor elke gemeente of overheidsorganisatie. Elke organisatie (tenant) heeft een volledig afgeschermde omgeving met eigen data, eigen configuratie en eigen gebruikersbeheer. Wat geldt voor één tenant heeft geen invloed op een andere.

De platformbeheerder configureert componenttypen, relatietypes, catalogi en rollenstructuren. Elke tenant richt vervolgens zijn eigen landschap in op basis van die gedeelde platformfundamentatie.

---

## Kernprincipes

**Expliciete relaties.** Het systeem verzint niets. Elke relatie in het model is bewust gelegd door een gebruiker. Wat niet geregistreerd is, bestaat niet in het model — dat is een signaal, geen stilzwijgende aanname.

**Score als enige lifecycle-driver.** De volledigheidscore is de enige maatstaf voor de lifecycle-status van een component. Geen tweede berekening, geen parallelle bron, geen omweg.

**Structurele integriteit.** Invarianten worden afgedwongen door het schema, niet door afspraken. Pre-productie is het goedkoopste moment om structureel correct te bouwen.

**Zichtbaarheid stimuleert volledigheid.** Een lege plaat, een ontbrekende eigenaar, een contract zonder leverancier — LIKARA maakt gaten zichtbaar zodat ze gedicht kunnen worden. Governance is geen rapportage achteraf maar een doorlopend signaal.

---

## Wat LIKARA niet is

LIKARA is geen vervanging van een Enterprise Architecture-tool (zoals Archi of BizzDesign), geen CMDB, en geen projectmanagementsysteem. Het is de **registratie-, communicatie- en governancelaag** die naast bestaande tooling bestaat — toegankelijk voor iedereen in de organisatie, niet alleen voor de architect.

---

## Samenvattend

> LIKARA geeft organisaties één betrouwbare plek waar het ICT-landschap volledig en begrijpelijk is vastgelegd — zodat transities, migratiebesluiten en eigenaarschapsvragen altijd vanuit feiten worden beantwoord, niet vanuit aannames.
