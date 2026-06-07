# SESSIE_BRIEFING.md — CompliData V003

**Gegenereerd**: 2026-06-07

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V002 |
| Datum | June 2026 |
| Commit | f6b2fc5 |
| Tests | 45 passed · 4 TST-assen groen |
| TST-rapport | TST-V002-Validatierapport.md |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
956eb3e chore(dev): lokale-test-stack — COOKIE_SECURE dev-only + LOKAAL-TESTEN.md
b9bd71e feat(bwb): Applicatie-module-view + opties-endpoint (lijst/detail/formulier/acties)
61482fc feat(frontend): authenticated app-shell (topbar + sidebar) + dashboard-landing
4230c4c feat(frontend): login-view (launch-pagina + Keycloak-redirect)
5afdd01 feat(bwb): Checklistscore + Blokkade (Model A) + ADR-013 lifecycle-herberekening
```

---

## Prioriteiten volgende sessie

# NEXT_SESSION.md — CompliData V003

**Gegenereerd**: 2026-06-07
**Vorige build**: V003
**Laatste commit (vóór afsluiting)**: 956eb3e

---

## Stand van zaken (V003)

Volledige verticale slice werkt end-to-end (empirisch geverifieerd op de draaiende
stack):

- **Backend module-CRUD** voor alle 6 BWB-entiteiten (Applicatie, Datatype,
  Gebruikersgroep, Koppeling, Checklistscore, Blokkade) onder `vereist_permissie`,
  tenant-scoped (RLS + expliciete filter), cursor-paginering, domeinexceptie+handler.
- **ADR-013 lifecycle** (Model A): deterministische `herbereken_lifecycle` +
  transitie-gebaseerde auto-blokkade-invariant; `checklist_compleet` transient.
- **Opties-endpoint** (read-only enum-metadata).
- **Frontend**: LoginView (Keycloak-redirect), AppLayout (topbar/sidebar/Toast),
  Applicatie lijst/detail/aanmaken/bewerken/start-inventarisatie/verwijderen met
  rol-gating + 422/403/404/409-afhandeling. Module-loading via Optie A
  (`@modules`/`@`-aliassen + cross-root-barrels).
- 323 backend-tests + 38 frontend-tests groen; `docs/LOKAAL-TESTEN.md` beschrijft de
  geverifieerde lokale doorklik-route.

---

## Top-5 prioriteiten volgende sessie

1. **Child-entiteit-views** binnen Applicatie-detail: Datatype, Gebruikersgroep,
   Koppeling (lijst + aanmaken/bewerken/verwijderen, ouder = de applicatie). Volg
   het Applicatie-module-view-patroon (DataTable, opties, `labels.js`, rol-gating).
2. **Checklistscore- + Blokkade-views** (lifecycle zichtbaar maken): scoren per
   vraag, blokkade-opvolging, lifecycle-Tag die meeschakelt (geblokkeerd/migratieklaar).
3. **OP-7 — canoniek 401/403/422 gelijktrekken** (nu: 404/403/409 canoniek; 401 en
   422 nog FastAPI-default). Eén `RequestValidationError`/auth-handler → `{fout:{…}}`.
4. **OP-3 — refresh-token-subsysteem** (`/auth/refresh`, server-side opslag, rotatie;
   sessie verloopt nu na 15 min).
5. **OP-4 — RP-initiated logout** via Keycloak end-session.

---

## Openstaande beslissingen

- Per-entiteit opties-endpoints vs. één gecombineerd metadata-endpoint voor de
  child-entiteiten.
- 422-canonisatie (OP-7) raakt álle endpoints → expliciet ADR-besluit vóór uitvoering.

---

## Bekende risico's en aandachtspunten (vervolgpunten)

- **CLAUDE.md onjuist**: "test mode — auth stub, auto-seed" klopt niet —
  `COMPLIDATA_TEST_MODE` is géén auth-stub en seedt niets (alleen origin/rate-limit).
  Rechtzetten in CLAUDE.md.
- **`tenantSlug`-bug** (`store/auth.js`): getter leest `user.tenant_slug`, maar
  `/auth/me` geeft `tenant_id` → altijd null. Raakt `useTheme`/per-tenant-thema's.
- **ADR-009 enum-voetnoten ↔ code** synchroniseren (`hostingmodel` 7, `migratiepad` 6,
  `protocol` = enum). Code is leidend.
- **IMPLEMENTATIEPLAN.md / SESSIE_BRIEFING.md** bevatten stale V001-snapshots.
- **Frontend bundle >500 kB** (DataTable) → route-level lazy-loading.
- **OP-13** platform-tabel-grants / **OP-14** dev-credentials (changeme_dev) vóór productie.

---

## Technische schuld

- 401 + 422 nog niet in canoniek `{fout:{…}}` (OP-7).
- Live DB-cascade + lifecycle-keten alleen structureel getest (offline-grens);
  eenmalig empirisch bevestigd in V003.
- SyntaxWarning in overgenomen framework-skill (ms365-tenant-manager) — geaccepteerd,
  buiten CompliData-scope.

---

## Geleerde patronen deze sessie (verwerkt in complidata-skills)

- Frontend-module-loading Optie A + cross-root-barrels (`@/primevue`,
  `@/composables/router`) — `complidata-frontend`.
- Domeinexceptie+handler-patroon, foutformaat-conventie, route-volgorde,
  opties-/afwijkende-CRUD — `complidata-backend`.
- ADR-013 lifecycle + keyset-cursor + enum-single-source — `complidata-db`.
- OP-6 afgedekt, rol-gating-affordance, COOKIE_SECURE dev-vs-prod, test-mode≠auth-stub
  — `complidata-security`.
- Frontend-testopzet + offline-grens — `complidata-tests`.


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — CompliData V003"
4. Wacht op START: [naam] van Bert
