# NEXT_SESSION.md — CompliData V004

**Gegenereerd**: 2026-06-07
**Vorige build**: V004
**Laatste commit (vóór afsluiting)**: 237b036 (gen_build bumpt hierna)

---

## Stand van zaken (V004)

Sessie CD003–CD012 bovenop de V003-slice:

- **Child-entiteit-views** (Datatype/Gebruikersgroep/Koppeling) als secties in
  `ApplicatieDetail` (Dialog-CRUD, geen child-routes). [CD003]
- **Checklist-scoringslijst** (inline, join op `vraag_code`) + **Blokkade-sectie**
  (read + PATCH) + **lifecycle-indicator** (backend-afgeleid). [CD004]
- **Canoniek foutcontract afgehecht** (ADR-014): 401/403/404/409/429 → `{"fout":{…}}`,
  422 bewust native. [CD005/CD009]
- **`tenantId`-fix** (OP-16). [CD006]
- **Refresh-token-subsysteem** (ADR-015, Redis + rotatie) + **single-flight
  refresh-on-401**. [CD007]
- **RP-initiated logout** + **`id_token_hint`** voor naadloze redirect (OP-4). [CD008/CD010]
- **Blokkade-`opgelost` volledig afgeleid** (ADR-016, reconciliatie ADR-013 B1). [CD011]
- **Route-level lazy-loading** — bundle 751 → 212 kB entry, >500 kB-waarschuwing weg. [CD012]
- **357 backend-tests + 83 frontend-tests groen**; geen migraties deze sessie.

---

## Top-5 prioriteiten volgende sessie (Bert prioriteert)

1. **Dashboard-inhoud** — voortgang/statistieken/open blokkades, tenant-breed.
2. **Blokkadesoverzicht tenant-breed** (los van één applicatie).
3. **Applicatieregister** filter/sortering.
4. **Docs-schuld wegwerken** — ADR-009-enums ↔ code synchroniseren; stale
   IMPLEMENTATIEPLAN.md / SESSIE_BRIEFING.md actualiseren. (CLAUDE.md test-mode al
   gecorrigeerd in V004.)
5. **Audit-trail (ADR-006)** — unblock voor de auditlog-view.

---

## Openstaande opvolgpunten (volledige onderbouwing: `CompliData_openstaande-vervolgstappen.md`)

**Productie/ops (vóór productie):**
- **OP-3-realm-hardening** — `revoke-refresh-token` aan in de realm; anders is de
  reuse-detectie (ADR-015 B3) niet actief. Koppelen aan **OP-14** (dev-credentials).
- **OP-13** platform-tabel-grants.
- **ADR-016-data-pass** — bij gevulde DB controleren + evt. herbereken-pass (Laag 5).

**Functioneel/architectuur:**
- **Koppeling OR-filter** — `?applicatie_id=` (bron OF doel) + index, indien volumes
  groeien (mogelijk mini-ADR).
- **Laag 4-schermen** — Dashboard, register-filter, 12-categorie-tabs,
  blokkadesoverzicht, koppelingenkaart, auditlog (geblokkeerd op audit-trail),
  gebruikersbeheer.
- **Laag 2/3** — tenant-onboarding, audit-trail (ADR-006), export Excel/CSV + PDF,
  MinIO (ADR-008).
- **Laag 5** — live DB-/RLS-test, smoke-test uitbreiden, branding-tokens,
  `useTheme`-activatie (getter `tenantId` staat klaar).

**Docs-schuld:**
- ADR-009 enum-voetnoten ↔ code (incl. DatatypeCategorie 6 vs 5); stale
  IMPLEMENTATIEPLAN/SESSIE_BRIEFING.

---

## Afgehecht deze sessie (uit de open lijst)

OP-7 (foutcontract: 401/403/429 canoniek, 422 bewust native), OP-16 (tenantSlug→tenantId),
OP-3 (refresh — mits realm-hardening apart), OP-4 (logout + id_token_hint),
ADR-013-reconciliatie (ADR-016), OP-19 (bundle), 403 `TENANT_MISMATCH`, 429-envelope.

---

## Geleerde patronen deze sessie (verwerkt in complidata-skills, V004-secties)

- `complidata-frontend` — secties-in-detail, inline scoringslijst (`vraag_code`),
  systeem-afgeleide view (read-only badge), gecoördineerde refetch, single-flight
  refresh-on-401, route-lazy-loading.
- `complidata-backend` — opties-endpoints, platform-breed referentie-endpoint,
  canoniek foutcontract (`HTTPException`-subclass), ADR-016-guard.
- `complidata-security` — Keycloak-refresh+Redis, RP-logout+`id_token_hint`, 401/403
  canoniek, `revoke-refresh-token`-voorwaarde.
- `complidata-db` — ADR-016-reconciliatie, ChecklistVraag-referentiedata, data-pass-discipline.
- `complidata-tests` — empirische stack-verificatie, regressie-borging, single-flight-testopzet.
