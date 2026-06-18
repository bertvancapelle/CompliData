# ADR-025 — Applicatie-centrische praatplaat (logisch afhankelijkheidsinzicht)

**Status:** Voorstel (open subknopen nog te beslissen)
**Datum:** 2026-06-16
**Relatie:** Leeslaag bovenop het getypeerde relatiemodel (ADR-023). Leunt voor ring 2 op het partijenregister (ADR-024). **Expliciet onderscheiden van Fase G (Open Exchange export)** — zie context.
**Invariant (ongewijzigd):** score blijft de enige lifecycle-driver — de engine wordt niet geraakt. Puur read-only, afgeleid.

---

## Context / aanleiding

ArchiMate- en EA-tooling is gebouwd voor de architect: formele notatie, alle elementtypen, technische relatietermen. Wat in veel organisaties juist **mist** is een **begrijpelijke praatplaat** voor een niet-technisch publiek (teamleider, proceseigenaar, bestuurder): inzage in de werking van het landschap zonder jargon. Dit ADR vult dat gat.

**Onderscheid met Fase G.** De Open Exchange export (ADR-023, geparkeerd) dient *architect-interoperabiliteit*: het model naar Archi/een EA-tool. Dat levert juist het technische beeld dat we hier willen vermijden. De praatplaat is een **aparte inzicht-/communicatielaag** bovenop dezelfde data, met een ander publiek. Beide mogen bestaan; ze zijn niet hetzelfde en vervangen elkaar niet.

De onderliggende data is er al: getypeerde elementen, getypeerde relaties (waaronder koppelingen en `draait_op`), en — met ADR-024 — de beheerpartijen. De **Koppelingenkaart** is de kiem hiervan. De waarde zit niet in méér data, maar in **weglaten, hertalen en focussen**.

---

## Besluit (kern)

1. **Applicatie-centrische 360°-view.** Eén applicatie in het midden, met daaromheen **vier ringen** die de organisatie wil begrijpen. Per applicatie opgebouwd; doordat elke applicatie zo'n plaat heeft, ontstaat applicatie-voor-applicatie inzicht in het hele landschap — zonder ooit de onleesbare "alles-in-één"-plaat te tekenen.
2. **Vier ringen rond de centrale applicatie:**
   - **Andere applicaties** — waar deze mee koppelt / van afhangt ("gebruikt" / "wordt gebruikt door").
   - **Beheerorganisatie** — wie welke beheerrol vervult (afdeling/persoon/leverancier), "wordt beheerd door" (uit ADR-024).
   - **Contracten** — welke contracten gelden voor deze applicatie ("valt onder contract").
   - **Infrastructuur** — waarop ze draait ("draait op").
3. **Diepte 1 + doorklik-hercentreren.** De plaat toont alleen de directe ring rond de gekozen applicatie. Klik op een buur (applicatie, of via doorklik infrastructuur) → de plaat **hercentreert** op die node. Zo wandel je door het landschap; elke plaat blijft leesbaar.
4. **Gewone taal, geen ArchiMate-notatie.** Relatietermen worden hertaald (geen "assignment/serving/realization", wél "draait op", "gebruikt", "wordt beheerd door", "valt onder contract"). Standaard niet alle elementtypen tonen — alleen wat een leek herkent.
5. **Doel:** transitie, migratie, uitfaseren — "wat raakt het als deze applicatie verschuift of verdwijnt", in begrijpelijke vorm.

---

## Model in detail

### Schematisch (één applicatie centraal, vier ringen, diepte 1)
```
         [andere applicaties]
                  │
 [contracten] — (APPLICATIE) — [infrastructuur: draait op]
                  │
        [beheerorganisatie: afdeling/persoon/leverancier]
```
Klik op een knoop → die wordt het nieuwe centrum (hercentreren).

### Ring → relatie-mapping (afgeleid uit bestaande relaties; geen nieuwe relaties)
- **Andere applicaties** ← de koppeling-/afhankelijkheidsrelaties tussen applicatie-componenten (beide richtingen, met leesbaar label).
- **Beheerorganisatie** ← de ADR-024 verantwoordelijkheid-relatie (partij → applicatie, met rol). *Beschikbaar zodra ADR-024 er is.*
- **Contracten** ← het bestaande component↔contract-verband.
- **Infrastructuur** ← `draait_op` (host→gehoste).

### Vertaalslag (de kern van de waarde)
- **Taal:** technische relatietypen → leesbare labels (bron: relatiekenmerk-catalogus + label-maps).
- **Selectie:** standaard alleen herkenbare elementtypen; formeel geraamte verborgen.
- **Focus:** één beginpunt + diepte 1, in plaats van "toon alles".

### Layout (waarom dit tractabel is)
Een ego-plaat op diepte 1 is **radiaal** (centrum + ringen) en daarom automatisch netjes te leggen — het ontwijkt het algemene auto-layout-/spaghettiprobleem dat de hele-landschap-plaat onmogelijk maakt. De vier ringen geven bovendien een natuurlijke sector-indeling.

---

## Invarianten

- **Read-only / engine onaangeroerd.** Puur een afgeleide inzicht-/communicatielaag bovenop bestaande relaties; voedt de engine niet. Geen schema/migratie verwacht (mogelijk een read-API + frontend). Dubbele engine-borging zoals gebruikelijk.
- **Geen afgeleide relaties** (ADR-023 besluit 7): de plaat *toont* bestaande, expliciet geregistreerde relaties; ze verzint er geen.
- **Een plaat is zo goed als de registratie.** Lege relaties → lege plaat. Bijvangst: het maakt registratiegaten zichtbaar.

---

## Gevolgen

- **Afhankelijkheid van ADR-024 voor ring 2.** De beheerorganisatie-ring bestaat pas zodra het partijenregister er is. Een eerste versie kan de andere drie ringen (applicaties, contracten, infrastructuur) al tonen; ring 2 komt erbij ná ADR-024. Natuurlijke fasering.
- **Verhouding tot de Koppelingenkaart** (subknoop): vervangt deze de Koppelingenkaart, breidt die uit, of staat ernaast?
- **Geen EA-tool.** Dit is bewust géén vervanger van een EA-tool; het is de communicatielaag. De Fase-G-export blijft de architect-route.
- **RBAC/audit:** read-only; waarschijnlijk hergebruik van een bestaande architectuur-/leespermissie (subknoop).

---

## Open subknopen (te beslissen vóór de bouw — met voorlopige default)

1. **Renderingtechniek + plek.** In-app radiale SVG/HTML-weergave, voortbouwend op de Koppelingenkaart. *Default: in-app radiale ego-graph; geen externe lib tenzij nodig.*
2. **Verhouding tot de Koppelingenkaart.** Vervangen / uitbreiden / ernaast. *Default: de praatplaat is de opvolger/uitbreiding van de Koppelingenkaart (één plek voor visueel inzicht), niet een tweede losse kaart.*
3. **Centrum-scope.** Alleen applicaties als centrum, of mag je ook hercentreren op infrastructuur/contract/partij? *Default: centrum primair applicatie; doorklik naar infrastructuur mag hercentreren (dan toont die node zijn eigen ringen), contract/partij voorlopig als bladknoop (geen eigen plaat) om scope te beperken.*
4. **Label-/taalmapping per relatietype** (welke leesbare term per ring/richting). *Default: vaste leesbare labels per ring, bron relatiekenmerk-catalogus + label-maps; bevestigen per relatietype.*
5. **RBAC.** Hergebruik de `ARCHITECTUUR`-leespermissie (uit F-2) of een eigen permissie. *Default: hergebruik `ARCHITECTUUR.LEZEN`.*
6. **Export/print** van een plaat (om daadwerkelijk te "praten" — PDF/PNG)? *Default: niet in v1; latere toevoeging.*
7. **Lifecycle-/status-kleuring** op de knopen (bv. de bestaande score-kleur of lifecycle-status tonen, voor migratie-inzicht)? *Default: ja, statuskleur op de knopen meenemen (read-only weergave; raakt de engine niet) — sluit aan op transitie/migratie-doel.*

---

## Bouw-fasering (indicatief, ná besluitvorming en ná Fase F)

1. **Read-API** — per applicatie de ringen ophalen (applicaties/contracten/infrastructuur bestaan al qua data; beheerorganisatie ná ADR-024).
2. **Frontend radiale praatplaat** — diepte 1, doorklik-hercentreren, leesbare labels, (optioneel) statuskleur.
3. **Ring 2 (beheerorganisatie)** toevoegen zodra ADR-024 is geland.
4. **Optioneel** export/print.

Elke slice read-only, met engine-onaangeroerd-borging en de gangbare gate-discipline.
