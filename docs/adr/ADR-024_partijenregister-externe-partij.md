# ADR-024 — Partijenregister en verantwoordelijkheidstoewijzing

**Status**: In uitvoering — slices 1–4 geland (DC011–DC013)
**Hoort bij**: ADR-023 (ArchiMate-uitlijning, element-supertype), ADR-021 (component-herfundering),
ADR-020 (contractregister), ADR-012 (tweelaags rollenmodel), ADR-026 (catalogus-typering).

> Dit document is in DC013 bijgewerkt naar de werkelijke bouwstand. De oorspronkelijke titel
> ("externe partij — leverancier-promotie") dekte alleen slice 1; het register omvat nu alle
> vier partij-aarden plus verantwoordelijkheidstoewijzing.

## Context

LIKARA registreert nu een volledig **partijenregister**: externe partijen, interne
organisaties, afdelingen en personen als first-class elementen binnen het ArchiMate-uitgelijnde
model (ADR-023). **Verantwoordelijkheid** ("wie doet wat") is registreerbaar via **roltoewijzing**
op componenten en contracten. ADR-020 modelleerde `leverancier` nog als losse tenant-tabel buiten
het element-/relatiemodel; ADR-024 promoveert dat tot een element-subtype `partij` en bouwt het
register stapsgewijs uit.

## Besluiten — samenvatting per slice

### Slice 1 — Externe partij (DC011, migraties 0026–0027)
*(0025 hoort bij ADR-026 — componenttype-typering — niet bij ADR-024.)*

- **Supertype `partij` als element-subtype.** Nieuwe `ElementType` `partij`, vaste typing
  `ELEMENT_ARCHIMATE_TYPING['partij']` = `business_actor` / `business` / `active`; de
  partitie-/dekkingstest (`test_archimate_fase_a`/`fase_d`) blijft sluitend.
- **Eén `partij`-subtabel** met aard-discriminator (shared-PK composiet-FK
  `(tenant_id, id) → element` ON DELETE CASCADE, FORCE RLS). Velden: `aard` (NOT NULL,
  `partij_aard_enum`), gedeelde contactvelden (`naam` NOT NULL; rest nullable), `soort` (optioneel).
  Géén aard-eigen sub-subtabel.
- **`partijsoort_optie`-catalogus** (platform-breed, GEEN RLS); seed: `leverancier` / `partner` /
  `ketenpartner`. De soort is optioneel op een partij (registratiegat).
- **Contract-leverancier hernomen naar het partij-element** (optie A — term "leverancier" blijft in
  het contract-domein): FK-target verschuift naar `(tenant_id, leverancier_id) → element`,
  ON DELETE RESTRICT, NOT NULL.
- **`element_type_enum ADD VALUE 'partij'`** als aparte, niet-transactionele migratie (0026) vóór de
  subtype-migratie (0027).
- Beheerscherm "Externe partijen" (in slice 2 hernoemd naar "Partijen").

### Slice 2 — Alle aarden + lidmaatschap (DC012, migratie 0028)

- Aarden **`organisatie`, `organisatie_eenheid`, `persoon`** in gebruik genomen op de `partij`-subtabel
  (de enum kende ze al; nu functioneel aanmaakbaar). `PartijAard` = `externe_partij` / `organisatie` /
  `organisatie_eenheid` / `persoon`.
- **Schema-borging lidmaatschap** via conditionele CHECKs: persoon/afdeling vereisen `organisatie_id`;
  `organisatie`/`externe_partij` mogen geen ouder hebben; `afdeling_id` alleen bij `persoon`.
- **Service-validatie** `partij_service._valideer_lidmaatschap` (cross-row, 422
  `ORGANISATIE_VERPLICHT` / `ONGELDIGE_ORGANISATIE` / `ONGELDIGE_AFDELING`): de organisatie is
  organisatie-achtig, de afdeling is een `organisatie_eenheid` binnen die organisatie.
- Eén **Partijen-beheerscherm** voor alle vier aarden (aard-filter; aard verplicht bij aanmaken en
  daarna vast); leden-overzicht (persoon/afdeling onder een organisatie), server-side sorteerbaar +
  gepagineerd.

### Slice 2b — Roltoewijzing (DC012, migraties 0029–0030)

- **`roltoewijzing`-tabel** — een **eigen tenant-tabel**, géén relatie-facade. Reden: de gewenste
  uniciteit `UNIQUE(tenant_id, partij_id, object_id, rol)` botst met `UNIQUE(tenant,bron,doel,type)`
  van de gedeelde `relatie`-tabel (meerdere rollen per (partij,object) als losse rijen).
- **Objecten** = `component` of `contract`; **bron** = elke partij-aard. Rol uit de **`beheerrol`**-
  catalogus (platform-breed, startset 7 rollen: Functioneel/Technisch/Applicatie/Contract-beheer,
  Product owner, Eigenaar, Proceseigenaar).
- Niets geforceerd: meerdere rollen van dezelfde partij op hetzelfde object, of meerdere partijen per
  rol, zijn allemaal losse rijen.
- **`VerantwoordelijkheidSectie`** op component-/contract-detail: toewijzen + tonen + verwijderen.
- **`PartijRollenSectie`** op partij-detail: overzicht van rollen per object.

### B6 — Organisatie als verwijzing op andere entiteiten (DC012, migraties 0031–0032)

- **`gebruikersgroep.organisatie_id`** → optionele FK naar element (aard=organisatie),
  ON DELETE SET NULL **kolom-specifiek** (PostgreSQL 15+, zodat de gedeelde `tenant_id` niet
  mee-genulld wordt).
- **`component.eigenaar_organisatie_id`** → idem. Beide tonen de gejoinde `Partij.naam` in
  lijsten/details (naam-in-read via alias); lijst-filter/sortering op de organisatie.

### DC013 — Contractpartij verbreed + roltoewijzing vanuit partij

- **Contractpartij verbreed** (commit 93aedc3, geen migratie): de contract-leverancier mag elke aard
  zijn **behalve `persoon`** — `TOEGESTANE_LEVERANCIER_AARDEN = {organisatie, organisatie_eenheid,
  externe_partij}`; persoon ⇒ 422 `ONGELDIGE_PARTIJ`. Vervangt de eerdere harde beperking tot
  `externe_partij`. (`contract_service._valideer_contractpartij`, voorheen `_valideer_externe_partij`.)
- **Roltoewijzing toevoegbaar vanuit het partij-detail**: `PartijRollenSectie` kreeg een
  "Rol toevoegen"-actie (zoekbaar object uit componenten + contracten, rol uit de `beheerrol`-
  catalogus) — symmetrisch met `VerantwoordelijkheidSectie`, zelfde endpoint, geen backend-wijziging.

## Gevolgen

- Het partijenregister is element-backed en doet mee in het relatie-/architectuurmodel. **Engine
  onaangeroerd**: partij, roltoewijzing en organisatie-verwijzingen voeden geen lifecycle/profiel/
  score/blokkade (offline import-afwezigheid + live trigger-afwezigheid geborgd); score blijft de
  enige lifecycle-driver.
- Migratieketen ADR-024: `0026` (enum) · `0027` (partij-subtabel + catalogus + contract-FK) · `0028`
  (lidmaatschap) · `0029` (beheerrol) · `0030` (roltoewijzing) · `0031` (gebruikersgroep-organisatie) ·
  `0032` (component-eigenaar-organisatie).

## Niet in scope / open punten

- **Contract-leverancier optioneel maken** (nu NOT NULL) — apart contract-spoor (incl.
  "leverancier onbekend"-signaal).
- **Roltoewijzing op meer object-typen** dan component/contract (bv. gebruikersgroep, werkpakket) —
  nu beperkt tot `{component, contract}`.
- **Organisatiestructuur** (persoon ∈ afdeling ∈ organisatie) is via de lidmaatschapsvelden
  geregistreerd; formele ArchiMate-aggregation-relaties hiervoor zijn geparkeerd.
- **Volledige rename van het contract-domein** naar "partij" (optie B) — bewust niet gedaan
  (blast-radius-minimalisatie).
- **Registratiegat-signalering** (object zonder rol; lege eigenaar-/groep-organisatie) — verzameld
  voor de signalerings-ADR; puur read-only, geen engine-poort.
- **ADR-025** (applicatie-praatplaat) en **ADR-027** (categorie-klaarverklaring) bouwen voort op dit
  register en wachten op de ADR-024-volledigheid.
