# LIKARA Changelog V018

**Datum**: 2026-06-22

## Wijzigingen

DC017 — platform-rebranding **CompliData/KILARA → LIKARA** (Logische ICT Kaart Afhankelijkheden
Relaties Analyse), canoniek dev-seed, Keycloak login-theme, dev-gebruikers en kaart-UX.

### Canoniek dev-seed (`be85709`)
- `_seed_bvowb_scenario` vervangt het Veldendam-scenario: BvoWB als shared-services
  dienstenprovider voor Gemeente Tiel/Culemborg/West Betuwe — 8 organisaties, 10 leveranciers,
  1 burger, 3 afdelingen, 36 personen, 12 applicaties, 15 contracten (incl. 3 DVO's),
  29 flows, 75 roltoewijzingen, 35 gebruikersgroepen, 267 scores.
- Scoringsplan: Zaaksysteem geblokkeerd, BRP migratieklaar, DMS/Klantportaal/Burgerzaken-suite
  deels, overige 7 concept.

### Keycloak login-theme + app-rename (`22a33b8`, `52d3308`, `eb1fe21`)
- Custom KC 24 login-theme met huisstijl (donkerblauw, wit kaartje, branding + tagline).
- CSS-fixes: volledige donkerblauwe achtergrond, verticaal gecentreerde kaart, titel verborgen,
  geen 100vh-stretch (KC 24 = klassieke `.login-pf-*` classes, niet PatternFly-5).

### LIKARA-rename + dev-gebruikers (`c6df5fb`)
- Theme `kilara`→`likara`, realm `loginTheme`/`displayName`, frontend header/login/tab-titel.
- 3 BvoWB dev-loginaccounts (j.devries/p.vandijk = medewerker, m.bakker = auditor) met vaste
  UUID's; `_seed_dev_gebruikers` koppelt ze aan hun persoon (ADR-029, hardcoded KC-subs).

### Laag 1 cleanup (`9e42855`)
- Alle user-visible/config/skills/docs "CompliData"/"KILARA" → "LIKARA"; KC-client
  `kilara-user-provisioning` → `likara-user-provisioning`; test-emails → `@likara.test`.
- Technische identifiers (realm-ID `complidata`, `cd-*`, `cd_app`, `/realms/complidata`,
  clientId `complidata-api/-ui`) bewust uitgesteld naar **Laag 2 (DC018)**.
- Historische changelogs `CompliData_Changelog_V001–V017` + TST-rapporten ongemoeid gelaten.

### Sessie-afsluiting DC017 (deze commit)
- Skills bijgewerkt met DC017-patronen (kaart-edge-groepering/master-detail, KOPPELING_DUBBEL,
  detail-navigatie watch-patroon, context-in-header, aard_in-filter, ongeordend-paar-filter,
  aard=burger, canoniek seed, KC login-theme, dev-gebruiker-provisioning).
- OPVOLGPUNTEN: DC017-blok (Laag 2, dode seed-functies, stale child-secties, soort-catalogus,
  STATE_ONGELDIG-pagina).
- V-bump V017→V018; nieuw changelog-patroon `LIKARA_Changelog_*` (historische blijven CompliData).

### Verificatie
- Frontend 555 groen + build/css groen; backend 860 passed (9 pre-existing DB-state/env-failures,
  o.a. OP-30 Secure-cookie env-test — identiek op schone HEAD, geen regressie).
- Live KC: theme, dev-users + rollen, provisioning-token HTTP 200, API health ok.
