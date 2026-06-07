# TST-V004 — Validatierapport

| Veld | Waarde |
|------|--------|
| Build label | V004 |
| Datum | 2026-06-07 |
| Vorige build | V003 |
| Kritieke bevindingen | 0 |

Deze sessie (CD003–CD012) leverde: child-entiteit-views in `ApplicatieDetail`
(Datatype/Gebruikersgroep/Koppeling), Checklistscore-scoringslijst + Blokkade-sectie
+ lifecycle-indicator, het canonieke foutcontract afgehecht (ADR-014: 401/403/404/
409/429 envelope, 422 native), `tenantId`-fix (OP-16), het refresh-token-subsysteem
(ADR-015) + RP-initiated logout met `id_token_hint` (OP-3/OP-4), de
blokkade-`opgelost`-reconciliatie (ADR-016) en route-level lazy-loading (OP-19).
Geen migraties deze sessie. Validatie omvat de 4 backend-assen **plus** de
frontend-poorten.

## Backend — 4 assen (CONTRIBUTING.md §6)

| As | Commando | Verwacht | Resultaat |
|----|----------|----------|-----------|
| 1 — py_compile | `find … \| xargs py_compile` | 0 syntaxfouten | **Geslaagd** — 0 fouten (alleen een `SyntaxWarning` in een overgenomen framework-skill-script, geen projectcode) |
| 2 — pytest | `python3 -m pytest backend/tests/ modules/ -q` | alle groen | **Geslaagd** — **362 passed** (incl. CD013-A backup-stap-tests) |
| 3 — Alembic | `alembic heads` / `branches` | 1 head, 0 branches | **Geslaagd** — 1 head `0002_platform_tenant`, 0 branches (geen nieuwe migratie deze sessie) |
| 4 — referentie-grep | grep `Eraneos\|compliman\|cm_` | 0 hits | **Geslaagd** — 0 hits (incl. `frontend/src/`, `frontend/tests/`, `.vue`, `docs/adr/`) |

## Frontend — poorten

| Poort | Verwacht | Resultaat |
|-------|----------|-----------|
| `vite build` | 0 fouten, 0 chunks >500 kB | **Geslaagd** — 0 waarschuwingen; entry `index` 212 kB (was 751 kB), PrimeVue-vendor `tag` 387 kB, `ApplicatieDetail` lazy 65 kB |
| `vitest run` | alle groen | **Geslaagd** — **83 passed** (15 bestanden) |

## Dekking deze sessie (samengevat)

- **Frontend**: child-secties-in-detail (Dialog-CRUD, geen child-routes); inline
  Checklist-scoringslijst (join op `vraag_code`, per-rij opslaan + feedback);
  Blokkade-sectie (read + PATCH, geen toevoegen/verwijderen, `opgelost` read-only);
  lifecycle-indicator (backend-afgeleid); gecoördineerde refetch via
  `defineExpose`/emits; a11y in Dialogs; single-flight refresh-on-401; lazy-loading.
- **Backend**: per-entiteit opties-endpoints; platform-breed `GET /checklistvragen`
  (geen RLS, cross-tenant-test); canoniek foutcontract via `HTTPException`-subclass-
  excepties (401/403); refresh-subsysteem (Redis-handle `{refresh_token,id_token}`,
  rotatie); RP-initiated logout (`id_token_hint`); ADR-016-guard (handmatig `opgelost`
  → 409).
- **Empirische verificatie** (draaiende stack): `refresh_token` aanwezig + refresh-grant
  roteert (CD007); logout-confirm-scherm zonder hint vs. 302 mét hint (CD008/CD010);
  end-session-config (CD008).

## ADR's deze sessie

- **ADR-014** — canoniek foutformaat (401 gelijk, 422 native); afgehecht in CD009 (403
  TENANT_MISMATCH + 429).
- **ADR-015** — refresh-token-subsysteem (Keycloak-gedelegeerd, Redis).
- **ADR-016** — blokkade-`opgelost` volledig afgeleid (amendeert ADR-013 B1).

## Geaccepteerde afwijkingen / open noten

- **422 = native FastAPI** `{detail:[…]}` — canoniek besluit (ADR-014 B2), geen wrapper.
- **`revoke-refresh-token` staat UIT** in de realm → reuse-detectie (ADR-015 B3) nog
  niet actief; app bewaart wel het nieuwste token. Opvolgpunt OP-3-realm-hardening (OP-14).
- **ADR-016-data-pass** alleen tegen dev-DB (0 blokkades) gevalideerd; opnieuw toetsen
  bij gevulde DB (Laag 5).
- **`checklist_compleet`** transient (ADR-013 B4) — niet als ruststatus getoond.
- ADR-009 enum-voetnoten ↔ code nog niet gesynchroniseerd (code leidend) — docs-schuld.
