# TST-V006 — Validatierapport

| Veld | Waarde |
|------|--------|
| Build label | V006 |
| Datum | 2026-06-10 |
| Vorige build | V005 |
| Kritieke bevindingen | 0 |

Deze sessie (CD025–CD038) leverde: **ADR-019** — configureerbaar antwoordveld per
checklistvraag (fasen 2A–2E + dev-seed); **ADR-012 Addendum A** —
`PlatformEntiteit.CHECKLISTCONFIG`; de **hardening-bundel** (O2: 7.5 BIO2 → BBN,
en de verificatie van OP-4/OP-7/OP-16 die al opgelost bleken); en een read-only
**OPVOLGPUNTEN-verificatie-sweep** (OP-19 gemitigeerd; OP-13/20/21/22 getoetst).
Twee additieve migraties: `0003_antwoordconfig` (datamodel) en `0004_bio2_bbn`
(data, soft-deactivate). Validatie omvat de 4 backend-assen **plus** de
frontend-poorten.

## Backend — 4 assen (CONTRIBUTING.md §6)

| As | Commando | Verwacht | Resultaat |
|----|----------|----------|-----------|
| 1 — py_compile | `find … \| xargs py_compile` | 0 syntaxfouten | **Geslaagd** — 0 fouten (alleen een `SyntaxWarning` in een overgenomen framework-skill-script `ms365-tenant-manager`, geen projectcode) |
| 2 — pytest | `python3 -m pytest backend/tests/ modules/ -q` | alle groen | **Geslaagd** — **519 passed** |
| 3 — Alembic | `alembic heads` / `branches` | 1 head, 0 branches | **Geslaagd** — 1 head `0004_bio2_bbn`, 0 branches |
| 4 — referentie-grep | grep `Eraneos\|compliman\|cm_` | 0 hits | **Geslaagd** — 0 hits (incl. `frontend/src/`, `modules/`, `docs/adr/`) |

## Frontend — poorten

| Poort | Verwacht | Resultaat |
|-------|----------|-----------|
| `vite build` | 0 fouten, geen chunk >500 kB | **Geslaagd** — géén ">500 kB"-waarschuwing; grootste chunk `column` (PrimeVue DataTable, lazy) 384 kB, entry `index` 164 kB (OP-19 gemitigeerd) |
| `vitest run` | alle groen | **Geslaagd** — **151 passed** (21 bestanden) |

## Scope van de validatie (deze sessie)

- **ADR-019 (2A–2E + dev-seed)** — antwoordtype + optie-catalogus + `antwoord_waarde`;
  read/write + validatie (structureel 422 native, semantisch 422-envelope); scoring-UI
  ("Afgehandeld"); platform-config-endpoints + RBAC; sessietype-bewuste SPA-auth +
  beheer-UI. **Engine byte-identiek door alle fasen** — live dev-tellingen
  **lifecycle 1·4·3·4** en **blokkades 7·1·2** ongewijzigd (empirisch bevestigd na elke fase).
- **ADR-012 Addendum A** — `CHECKLISTCONFIG` (beheerder L/A/W, operator L, geen V);
  RBAC-matrixtest uitgebreid (4 × 2 × 4).
- **O2 (CD035)** — 7.5 → BBN via expand/contract (`0004_bio2_bbn`): BBN actief, legacy
  L/M/H inactief, 9 bestaande antwoorden 0 niet-resolvebaar, idempotent, engine ongemoeid.
- **OPVOLGPUNTEN-sweep** — OP-4/OP-7/OP-16 geverifieerd reeds opgelost (CD005/CD008/CD010);
  OP-19 gemitigeerd; OP-13/20/21/22 getoetst (blijven open).

## ADR's deze sessie

- **ADR-019** — configureerbare antwoordopties per checklistvraag (Aanvaard, CD025).
- **ADR-012 Addendum A** — `PlatformEntiteit.CHECKLISTCONFIG` (Aanvaard, CD031).

## Niet-blokkerende noten / geaccepteerde afwijkingen

- **Frontend-teardown-`DOMException`** (happy-dom thema-stylesheet-`fetch`, afgebroken bij
  window-teardown) op stderr — bekende ruis, **geen testfout** (alle 21 testbestanden groen).
- **OP-22** — de `gen_build`-DB-dump bevat nog het Keycloak-schema (hashes + client-secret),
  omdat Keycloak de `complidata`-database deelt. **Bewust geaccepteerd dev-risico**; vóór
  productie oplossen (backup scopen óf Keycloak in eigen DB/schema). Blijft als bekend risico
  in `OPVOLGPUNTEN.md`.
- **422 = native FastAPI** `{detail:[…]}` — canoniek besluit (ADR-014 B2); 401/403/404/409
  envelope.
- **Geparkeerd** (eigen traject): OP-3 + Keycloak `revokeRefreshToken` (code lijkt al grotendeels
  aanwezig — analyse-gate), OP-14 (deploy/secrets). Observaties O3/O4 open.
