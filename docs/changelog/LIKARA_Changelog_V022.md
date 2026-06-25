# LIKARA Changelog V022

**Datum**: 2026-06-25
**Sessie**: LI021

## Wijzigingen

### Test-hygiëne — live-DB-tests zelf-opruimend (`0c4371b`)
- Twee live-DB-tests ruimden hun rijen **inline** op i.p.v. in `finally` → lekten bij een falende
  assert hun fixtures (`CD052-db-*`/`AUDIT-SRV-*`) naar de dev-DB en vervuilden andere tests
  (vicieuze cirkel). Cleanup verplaatst naar `finally` (`test_component_contract_op_niet_applicatie_component`,
  `test_score_write_driver_plus_afgeleide_delen_correlatie`); opruimvolgorde behouden, asserties ongewijzigd.
- Geverifieerd: residu vóór == ná (geen nieuwe artefacten, ook bij falen); de vervuilings-cirkel is gebroken.

### Seed-verrijking — `_seed_bvowb_scenario` (data-only, idempotent) (`ae905c1`)
- **Infrastructuur** (technology-laag, kale componenten): Shared DB-server (database) onder
  Zaaksysteem/BRP/DMS, Shared fileshare (fileshare, bewust zonder eigenaar) onder DMS/Klantportaal,
  Extern SaaS-platform (saas_dienst) onder Vergunningensysteem — elk met een draait-op (assignment)-relatie.
- **Component-samenstelling** (aggregation): Burgerzaken-suite → Aangiften/Reisdocumenten/Verkiezingen
  (applicatie + eigenaar=BvoWB, kaal) → samenstelling-ring + onderdeel-van-impactrelatie zichtbaar.
- **Bewuste scope-gaten**: Archiefbeheer (applicatie zonder eigenaar) → "zonder eigenaar"-teller = 1;
  Klantportaal uit `org_apps` → na schone reseed uitsluitend door de organisatieloze Burgers-groep geserved.
- Engine onaangeroerd (infra zonder profiel; nieuwe apps op de `concept`-vloer, 0 scores/0 blokkades).

### Landschapskaart-vertrekpunt — fase A (achterkant-kern) (`fec08d5`)
- **Set-scoped subgraaf**: POST `/landschapskaart/subgraaf` `{component_ids, diepte}` →
  `LandschapskaartResponse` gescoopt op S + 1 hop. `haal_grafdata_op(..., component_ids=None)` =
  volledige graaf (back-compat); set-scoping via discovery-pass (`scope_ids` = S ∪ 1-hop-buren ∪
  org-hiërarchie ∪ eigenaar-orgs) + `_sc`-filter op de tenant-brede where-clausules. De
  organisatiestructuur-ring drijft op de rol-personen ván S.
- **Leverancier-filter** op `/componenten`: afgeleide EXISTS over beide paden (roltoewijzing
  technisch_beheer/contractbeheer OF association→contract.leverancier), keyset-paginering intact.
- **Eigenaar-edge** "is eigendom van" (organisatie→component): afgeleide read-only context-projectie uit
  `Component.eigenaar_organisatie_id`, alleen als de organisatie als knoop meekomt. Context — **niet** in
  `IMPACT_RINGEN`. Dekt het geparkeerde "scopebalk-tekent-organisaties"-spoor af.
- Additief/read-only; geen schema/migratie; dubbele engine-borging (import-afwezigheid + read-only
  bronscan) groen. +6 nieuwe tests groen.

### Skills / docs
- complidata-skills bijgewerkt (backend/frontend/ux/tests): kaart-schaalarchitectuur (set + 1-hop, nooit
  de volledige graaf); vertrekpunt = zoeken (leeg openen, selectie = componenten, org/leverancier =
  criteria); accumulerende sub-graaf-cache; "zoek-erop-dan-toon-het" (handmatig wint); geen betuttelende
  scenario-regels; na `down -v` dev-seed handmatig; live-DB-drift ≠ residu.

## Bekende punten

- **8 pre-existing live-DB-failures** = **seed-drift** (tests verwachten dode-seed-rijen die
  `_seed_bvowb_scenario` niet maakt). De `finally`-hygiëne brak de residu-cirkel; de drift wordt door
  LI022-stap 1 (reset + seed-herijking) opgelost. Niet als opgelost gemarkeerd. Zie
  `docs/TST-V022-Validatierapport.md`.
