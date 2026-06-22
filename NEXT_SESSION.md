# NEXT_SESSION.md — LIKARA V018

**Gegenereerd**: 2026-06-22 (sessie DC017)
**Build**: V017 → **V018**
**Laatste commit vóór de afsluiting**: `9e42855` (Laag 1 cleanup CompliData/KILARA → LIKARA); de afsluit-commit (skills/OPVOLGPUNTEN/NEXT_SESSION/changelog/build) volgt hierop.
**Migratie head**: `0041` (`0041_partij_aard_burger`)
**Tests**: 860 backend passed + 555 frontend groen + `test:css-build` groen (9 pre-existing backend DB-state/env-failures, o.a. OP-30 Secure-cookie env-test — identiek op schone HEAD, geen regressie).

---

## Stand van zaken (V018) — LIKARA-rebranding + canoniek seed + login-theme + dev-gebruikers

Deze sessie (DC017):

- **Canoniek dev-seed** (`be85709`): `_seed_bvowb_scenario` vervangt Veldendam — BvoWB als
  shared-services dienstenprovider voor Tiel/Culemborg/West Betuwe (8 org, 10 leveranciers, 1 burger,
  36 personen, 12 apps, 15 contracten incl. 3 DVO's, 29 flows met namen, 75 roltoewijzingen,
  35 gebruikersgroepen, 267 scores; Zaaksysteem geblokkeerd, BRP migratieklaar).
- **Keycloak login-theme** (`22a33b8`, `52d3308`, `eb1fe21`): custom KC 24-theme (huisstijl,
  gecentreerde witte kaart, titel verborgen). KC 24 = klassieke `.login-pf-*` classes, niet PF5.
- **LIKARA-rename + dev-gebruikers** (`c6df5fb`): theme/realm/frontend/tab-titel; 3 BvoWB
  dev-accounts (j.devries/p.vandijk = medewerker, m.bakker = auditor) met vaste UUID's,
  `_seed_dev_gebruikers` koppelt aan persoon (ADR-029, hardcoded KC-subs).
- **Laag 1 cleanup** (`9e42855`): alle user-visible/config/skills/docs CompliData/KILARA → LIKARA;
  KC-client `kilara-` → `likara-user-provisioning`; test-emails → `@likara.test`.
- **Sessie-afsluiting DC017** (deze commit): skills + OPVOLGPUNTEN + V-bump V018 + nieuw
  changelog-patroon `LIKARA_Changelog_*` (historische blijven CompliData).

Score blijft de enige lifecycle-driver. **Reseed-risico opgelost**: het nieuwe seed-scenario maakt
flows mét namen (ADR-023a-conform).

---

## Top-prioriteiten volgende sessie (DC018)

1. **LIKARA Laag 2 rename** (eigen sprint) — technische identifiers: realm-ID `complidata` → `likara`,
   container-namen `cd-*`, DB-rol `cd_app`, image `complidata-api:local`, ENV `KEYCLOAK_REALM`,
   clientId `complidata-api`/`complidata-ui`, `kilara_provisioning_secret` → `likara_provisioning_secret`.
   Raakt compose/.env/init-db/conftest/RLS-rol → **reseed (`down -v`) verplicht** + verificatie.
2. **Dode seed-functies opruimen** in `dev_seed_testdata.py` (`_seed_applicatie`,
   `seed_landschapskaart_demo`, `_seed_koppelingen` e.a. — ongebruikt sinds `_seed_bvowb_scenario`).
3. **Stale child-secties bij detail→detail-hop** — child-secties in ComponentDetail/ApplicatieDetail
   laden in `onMounted` zonder `:key`; remount-fix doortrekken.
4. **ADR-030 contract-dekking per band** (design-checkpoint → bouw).
5. **Resterende open punten**: ADR-029 Fase 5 (`gereedmeld_recht`), ADR-023 Fase F-rest
   (E-8 + RBAC/audit), landschapskaart server-side ego-subgraaf, STATE_ONGELDIG → "sessie verlopen"-pagina,
   objecthistorie-diff id→naam-resolutie, soort-catalogus uitbreiden (Dienstenprovider/Samenwerkende gemeente),
   stale root `OPVOLGPUNTEN.md` (V012) consolideren.

---

## Bekende risico's en aandachtspunten

- **Dev-inlog** vereist de volledige stack (Keycloak); frontend draait buiten Docker
  (`cd frontend && npm run dev`, poort 3000, proxy → :8000). Migratie head dev-DB: `0041`.
- **Live KC-wijzigingen** (theme, client-rename, dev-users, emails) staan in het KC-volume; de
  gecommitte realm-JSON reproduceert ze bij een verse `--import-realm`.
- **OP-30** `test_auth_pkce` Secure-cookie test faalt omgevingsgebonden (vereist TST-env) — geen regressie.
- **`test:css-build` nog niet in CI** (los script) — CI-stap/pre-push-hook is de logische vervolgstap.
- **Eén tenant nu** — geen per-tenant-differentiatie ontwerpen (RBAC = één platform-brede matrix).

---

## Werkwijze (triggerdiscipline)

Elke opdracht-`.md` begint op **regel 1** met `START: [taaknaam]`. **`AKKOORD: commit`** is exclusief de
commit-trigger op een groen (gate-)rapport. Schema-/endpoint-/RBAC-/datamodel-rakende slices = **gate**
vóór commit; licht/additief = doorloop. CC verifieert zélf de groene staat vóór elke commit. Eén
vraag/advies tegelijk; functioneel beschrijven vanuit de gebruiker is de norm. Reset-procedure:
`docs/LOKAAL-TESTEN.md`. Startpunt volgende sessie: `docs/_output/LIKARA_Sessiestart_V018.zip` →
**LIKARA Laag 2 rename (DC018)**.
