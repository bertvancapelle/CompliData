# ADR-026 — Beheerbare ArchiMate-typering per componenttype

**Status**: Geaccepteerd
**Hoort bij**: ADR-021 (component-herfundering), ADR-023 (ArchiMate-uitlijning, Fase C/D/F),
ADR-012 Addendum C (`COMPONENTCONFIG`), ADR-014 (canoniek foutformaat 422).

## Context

De ArchiMate-typering per componenttype (`archimate_element` / `laag` / `aspect`, dimensie
`componenttype` in `componentconfig_optie`) was seed-/code-vast en niet beheerbaar. Via het
platform-beheer ("Optie toevoegen") kon een componenttype ontstaan met **NULL-typering**: de
service `voeg_toe()` zette de drie velden niet, het schema droeg ze niet, en de dekkingstest
toetste de **seed-functie** (`bouw_componentconfig()`) — niet de live database. Zo'n
ongetypeerd type verscheen in de cross-element laagprojectie (ADR-023 F-2) als *ongetypeerd*
en viel buiten elke laag-filter, zonder dat een test het ving.

Dit ADR maakt de typering beheerbaar door de platformbeheerder én dicht het lek structureel.

## Besluit

1. **Gesloten, gedeelde, platform-brede element-whitelist.** `TOEGESTANE_ELEMENTEN` in
   `services/archimate_typing.py` — naast de al bestaande `TOEGESTANE_LAGEN` /
   `TOEGESTANE_ASPECTEN` (één gedeelde bron). Ruim opgezet (application/technology/business/
   implementation_migration); de **fysieke wereld** (facility/equipment/material) is bewust
   **niet** opgenomen. Alle reeds in gebruik zijnde element-namen (seed + `ELEMENT_ARCHIMATE_TYPING`)
   vallen binnen de set.
2. **Platform-breed, geen RLS.** De catalogus blijft één gedeelde set zonder `tenant_id`/RLS;
   de typering geldt voor alle tenants.
3. **Geldigheid via Pydantic field-validators** (ADR-014, native 422), elk veld **afzonderlijk**
   tegen zijn set — **geen combinatievalidatie** (welk element bij welke laag/aspect hoort wordt
   niet afgedwongen). `Create`/`Update` dragen `archimate_element`/`archimate_laag`/
   `archimate_aspect`; `Read` exposeert ze. `extra="forbid"` blijft.
4. **Volledigheid verplicht bij aanmaken** voor dimensie `componenttype` (model-validator);
   andere dimensies (`structuurrelatie_type`, `archimate_relatie`) laten de velden leeg.
5. **Service dicht het lek.** `voeg_toe()` zet de typering; `wijzig()` corrigeert naar geldige
   waarden; **leegmaken** van een componenttype-typering wordt geweigerd (`422 TYPERING_VERPLICHT`).
6. **Structurele backstop: conditionele DB-CHECK** (`ck_componentconfig_typering_volledig`,
   migratie `0025_adr026_typering_volledig`):
   *`dimensie <> 'componenttype' OR (archimate_element IS NOT NULL AND laag IS NOT NULL AND aspect IS NOT NULL)`*.
   Onvoorwaardelijk (geen `actief`-afhankelijkheid). Landde schoon (0 overtredende rijen).
7. **RBAC ongewijzigd.** Beheer onder `PlatformEntiteit.COMPONENTCONFIG` (platformbeheerder
   Aanmaken/Wijzigen; operator leest). Geen nieuwe permissie.
8. **Frontend.** Drie keuzevelden (element/laag/aspect) in toevoeg-/bewerk-dialog, alléén voor
   de sectie `componenttype`; drie tabelkolommen in de componenttype-tabel. Keuzelijsten uit de
   backend-bron (`/platform/componentconfig/typering-opties`) — niet in de Vue gehardcodeerd.

## Gevolgen

- Een componenttype kan nooit meer ongetypeerd bestaan — afgedwongen op drie lagen (schema,
  service, DB-CHECK) en geborgd door een **live-DB-dekkingstest** (naast de bestaande seed-test).
- **Engine onaangeroerd**: de typering voedt uitsluitend de architectuurprojectie (read); score
  blijft de enige lifecycle-driver. Machine-matig geborgd (import-afwezigheid + live-gedragstest).

## Niet in scope

- Combinatievalidatie element↔laag↔aspect.
- Per-tenant typering of -overrides.
- Wijziging van de vaste element-type-typing (`ELEMENT_ARCHIMATE_TYPING`, ADR-023 Fase D) —
  die blijft code-vast.

---

## Nadere besluiten (LI023)

Dit ADR is al geaccepteerd. De onderstaande punten leggen de eerder open uitwerkingsvragen vast als
besluit; ze sturen de geplande bouw-slice (verplichte typering in het componenttype-formulier).

1. **Gesloten lijst voor `archimate_element`.** Code-constante (gedeelde bron, zoals laag en aspect).
   De geldige ArchiMate-elementen zijn een vaste, taal-bepaalde set — geen organisatie-specifieke data.
2. **Volledigheids-mechanisme.** Het formulier is niet in te dienen zonder volledige typering — drie
   verplichte velden, net zoals naam verplicht is. De beheerder kan niet per ongeluk een incompleet
   type aanmaken. Service-side validatie + runtime-test als technische vangrail.
3. **Volledigheid: bij aanmaken.** Een componenttype zonder typering is direct al zinloos. Verplicht
   bij aanmaken, niet uitgesteld tot activeren.
4. **Bestaande NULL-rijen.** Er is alleen testdata (geen productiedata). De seed wordt bij de
   bouw-slice compliant gemaakt: elk componenttype in `seed_componentconfig` krijgt alle drie de
   typeringsvelden gevuld. Geen apart opschoonstap nodig.
5. **RBAC.** Typering bewerken = platformbeheerder (`PlatformEntiteit.COMPONENTCONFIG`). Geen aparte
   permissie nodig.
6. **Combinatievalidatie expliciet uit.** Het systeem dwingt niet af welk element bij welke
   laag/aspect hoort. De beheerder draagt de verantwoording voor een zinnige mapping.
