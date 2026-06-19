# SESSIE_BRIEFING.md — CompliData V016

**Gegenereerd**: 2026-06-20

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V016 |
| Datum | June 2026 |
| Commit | a4fd048 |
| Tests | 856 backend + 500 frontend groen |
| TST-rapport | TST-V016-Validatierapport.md |
| Kritieke bevindingen | 0 kritiek |

---

## Recente commits

```
a4fd048 feat(objecthistorie): ADR-029 — 'i'-knop op detailschermen (objecthistorie)
fea3768 feat(audit): ADR-029 Fase 3a — audit-view + naam-resolutie & naam/actie-filter
2ab091d feat(actor): ADR-029 Fase 3b — sub-stempeling + naam-resolutie (klaarverklaring + plateau)
c227e7a feat(gebruiker): ADR-029 Fase 4 — gebruikersbeheer-scherm (frontend)
0e6035b feat(gebruiker): ADR-029 Fase 2 — gebruiker-aanmaak backend (Keycloak provisioning + koppeltabel)
```

---

## Prioriteiten volgende sessie

# NEXT_SESSION.md — CompliData V016

**Gegenereerd**: 2026-06-20 (sessie DC015)
**Build**: V015 → **V016**
**Laatste feature-commit vóór de afsluiting**: `a4fd048` (objecthistorie — 'i'-knop op detailschermen); de afsluit-commit (docs/skills/build) volgt hierop.
**Migratie head**: `0038`
**Tests**: 856 backend + 500 frontend groen (1 pre-existing, omgevingsgebonden env-test `test_auth_pkce`)

---

## Stand van zaken (V016) — ADR-029 grotendeels gerealiseerd + objecthistorie

ADR-029 (gebruikersbeheer als primaire ingang; KILARA als bron van waarheid voor user-management,
brug Keycloak-login ↔ persoon-partij) is deze sessie grotendeels gebouwd:

- **Fase 2 — backend gebruikersaanmaak** (`0e6035b`): `gebruiker_persoon`-koppeltabel (migratie 0037),
  Keycloak Admin API-provisioning via dedicated service-account `kilara-user-provisioning`
  (least-privilege manage-users/view-users, client-credentials), server-gegenereerd eenmalig
  wachtwoord, niet-transactionele orphan-cleanup. Live-geverifieerd na realm-herimport (token + GET
  /users 200).
- **Fase 4 — gebruikersbeheer-scherm** (`c227e7a`): beheerder-only nav + lijst + aanmaak-dialog +
  eenmalig-wachtwoord-weergave (kopieerknop, nergens gepersisteerd).
- **Fase 3b — sub-stempeling + naam-resolutie** (`2ab091d`): `verklaard_door_sub` (klaarverklaring,
  migratie 0038) + plateau `bevestigd_door` {sub,email}; gedeelde `actor_resolutie`-helper
  (sub→persoon.naam, e-mail-fallback, historische rijen ongemoeid); read-side
  `verklaard_door_naam`/`bevestigd_door_naam`. ADR-027 wijzigingshistorie bijgewerkt.
- **Fase 3a — audit-view** (`fea3768`): `actor_naam`-batchverrijking (N+1-vrij) + actie-filter +
  naam-filter (naam→sub); nieuwe AuditTrailView (beheerder/auditor).
- **Objecthistorie** (`a4fd048`): `GET /objecthistorie/{type}/{id}` met **toegang-volgt-object**
  (geen AUDITLOG-gate; per-type leespermissie + 404 no-leak) + herbruikbaar `ObjectHistoriePaneel`
  ('i'-knop) op 8 detailschermen (component/applicatie/contract/partij/plateau/work_package/
  deliverable/gap), per-record diff met NL-veldlabels, "Meer laden".
- **Dev-seed-fix** (`572aa4c`): `dev_seed_testdata.py` crashte bij reseed op de met migratie 0034
  verwijderde `eigenaar_naam`/`leverancier`-kwargs.

Score blijft de enige lifecycle-driver — elke nieuwe schakel staat náást de engine, geborgd (offline
import-afwezigheid + live geen-mutatie). Skills security/backend/frontend bijgewerkt naar V016 met de
DC015-patronen (service-account-provisioning, eenmalig-geheim, orphan-cleanup, sub-stempeling +
actor_resolutie, naam→sub-filter, objecthistorie-paneel, toegang-volgt-object).

---

## Top-prioriteiten volgende sessie

1. **ADR-029 Fase 5** — `gereedmeld_recht` (per-type persoon × componenttype) + per-type check in de
   klaarverklaring-service. **Laatste open ADR-029-fase.** (Schema-rakend → gate.)
2. **ADR-023 Fase F-rest** — checklist-consistentiecheck technische plaatsing (E-8, deferred) +
   resterende RBAC/audit nieuwe entiteiten.
3. **Landschapskaart server-side ego-subgraaf** (aparte slice): `?center=<id>&diepte=1|2` i.p.v. de
   volledige tenant-graaf. Vereist nieuw endpoint-contract.
4. **KILARA — codebase-rename** (geparkeerd, DC013): product-/codenaam doorvoeren.

**Kleine follow-ups (DC015):**
- Dode backend-proxy-properties `Applicatie.eigenaar_naam`/`.leverancier` (`models.py:382/386`) —
  inert, opruimbaar in een aparte backend-taak.
- Naam-filter audit-view eventueel als ZoekSelect-op-personen (nu vrije-tekst search-semantiek).
- id→naam-resolutie in de objecthistorie-diff (`*_id`-velden tonen nu de gelogde id-waarde).

---

## Bekende risico's en aandachtspunten

- **Reseed na `down -v`**: de dev-seed (`docker exec -w /app cd-api python3 dev_seed_testdata.py`) is
  handmatig en nu gefikst; live-tests die seed-data nodig hebben falen tot de reseed is gedraaid.
- **Realm-herimport** is nodig na een wijziging in `keycloak/realms/complidata-realm.json`
  (`down -v && up -d`) — bv. de `kilara-user-provisioning`-client.
- **Pre-existing env-test** `test_auth_pkce` (OP-30, Secure-cookie, DB-onafhankelijk) — omgevingsgebonden, in deze omgeving groen.
- **Eén tenant nu** — geen per-tenant-differentiatie ontwerpen (RBAC = één platform-brede matrix; catalogi gedeeld). RLS blijft technisch fundament.

---

## Werkwijze (triggerdiscipline)

Elke opdracht-`.md` begint op **regel 1** met `START: [taaknaam]`. **`AKKOORD: commit`** is exclusief de
commit-trigger op een groen (gate-)rapport. Schema-/endpoint-/RBAC-rakende slices = **gate** vóór commit;
licht/additief = doorloop. CC verifieert zélf de groene staat vóór elke commit. Eén vraag/advies tegelijk;
functioneel beschrijven vanuit de gebruiker is de norm. Reset-procedure: `docs/LOKAAL-TESTEN.md`.
Startpunt volgende sessie: `docs/_output/CompliData_Sessiestart_V016.zip` → **ADR-029 Fase 5**.


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — CompliData V016"
4. Wacht op START: [naam] van Bert
