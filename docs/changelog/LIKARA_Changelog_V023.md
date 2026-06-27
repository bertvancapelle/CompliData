# LIKARA Changelog V023

**Datum**: 2026-06-27
**Sessie**: LI022 — Landschapskaart Fase B (set-gestuurd) + hygiëne/rename
**Baseline**: V022 (`55ff90d`)

## Wijzigingen

### Landschapskaart Fase B

- **Set-gestuurd laadpad + `subgraaf` api-client** (`10bb35e`, slice 0+1)
  - De Landschapskaart opent voortaan **leeg** (beginscherm) i.p.v. de volledige tenant-graaf te laden.
  - Niet-lege set → `POST /landschapskaart/subgraaf` (set + 1-hop); bij elke set-mutatie wordt de hele
    set opnieuw opgehaald (idempotent, geen incrementele merge).
  - **"Toon het hele landschap"** is een bewuste, aparte actie (geen default van een lege set), mét een
    echte voortgangsteller **"X van N"** (telt op verwerkte data in chunks; geen tijd-spinner).
  - `modus` 0 = `'leeg'` (beginscherm); **"Begin opnieuw"** = enige harde reset → terug naar leeg.
  - Nieuwe api-client `api.landschapskaart.subgraaf(component_ids, diepte)`.
  - Tests via strategie A (mountView laadt de "volledige" modus; één setter voedt full-load én
    subgraaf-mock; nieuwe bedrading-tests apart). Frontend-suite 654 → **663** groen.

- **Context-routes naar componenten** (`509e9ca`, slice 2a) — databron voor de "Via context"-ingangen:
  - `GET /contracten/{id}/componenten` — ALLE aan een contract gekoppelde componenten, **incl. kale/
    profielloze** (de `/applicaties`-INNER-join op `ComponentProfiel` liet die wegvallen). Nieuw endpoint
    naast `/applicaties` (dat ongemoeid blijft); engine-ontkoppeld.
  - `GET /gebruikersgroepen/contexten?zoek=` — distinct `(organisatie, afdeling)`-picker met
    component-telling, doorzoekbaar (begrensde afgeleide lijst, bewust ongepagineerd).
  - `GET /gebruikersgroepen/contexten/componenten?organisatie_id=&afdeling=` — componenten voor één
    context; nullable-veilige match (`IS NOT DISTINCT FROM`) dekt de lege-organisatie-casus ("— / Burgers").
  - RBAC hergebruikt `CONTRACT.LEZEN` + `GEBRUIKERSGROEP.LEZEN` (geen nieuwe entiteit). Dubbele
    engine-borging (offline import-/bronscan + live no-mutation). Backend-suite 904 → **910** passed.

### Hygiëne / rename / borging

- **8 stale live-DB-tests herijkt** op de verrijkte `_seed_bvowb_scenario` (`d6cd59f`) — de seed bleef
  onaangeroerd; de tests bewogen mee. Backend van 896 + 8 failers → 904 passed / 0 failers.
- **Skill-laag hernoemd `complidata-* → likara-*`** (`8b8a8b2`, `git mv`, historie behouden) + nieuwe
  eigenstandige skill **`likara-werkprotocol`** (samenwerkings-werkprotocol, 9e verplichte sessiestart-skill).
- **Laag-2 identifier-rename geborgd als opvolgpunt** (`6043094`): de gedragsbepalende identifiers
  (`complidata-api`-clientId, `COMPLIDATA_TEST_MODE`, `cd_`-familie, lokale `~/complidata/`-paden) als
  aparte, gecoördineerde slag.

### Sessie-afsluiting (V023)

- **Generators meegerenamed**: `gen_build.py` (REQUIRED_DIRS/REQUIRED_SKILLS) + `gen_sessiestart.py`
  (CURATED_SKILLS) + `gen_sessiestart_md.py` verwezen nog naar `.claude/skills/complidata/` → bijgewerkt
  naar `.claude/skills/likara/likara-*` (de rename had ze gemist; gen_build zou anders falen). De lokale
  `~/complidata/`-backup-paden zijn bewust behouden.
- Skills bijgewerkt (`bijgewerkt: V023`): likara-frontend (set-gestuurd kaart-laadpad), likara-backend
  (context→componenten read-endpoint-patroon), likara-tests (strategie-A testmigratie + ast-docstring-bronscan).
- NEXT_SESSION: volledig slice-2b-ontwerp + herziene slice-planning vastgelegd.

## Commits (V022 → V023)

- `509e9ca` feat(landschapskaart): contract- en gebruiker-context routes naar componenten (slice 2a)
- `10bb35e` feat(landschapskaart): set-gestuurd laadpad + subgraaf api-client (slice 0+1)
- `6043094` docs: Laag-2 identifier-rename als opvolgpunt geborgd
- `8b8a8b2` docs(skill): rename complidata→likara skill-laag + likara-werkprotocol
- `d6cd59f` test(hygiene): herijk 8 stale live-DB-tests op de verrijkte seed
