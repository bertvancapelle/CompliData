# TST-V003 — Validatierapport

| Veld | Waarde |
|------|--------|
| Build label | V003 |
| Datum | 2026-06-07 |
| Vorige build | V002 |
| Kritieke bevindingen | 0 |

Deze sessie leverde: P5 Applicatie-CRUD + child-entiteiten (Datatype/
Gebruikersgroep/Koppeling) + Checklistscore/Blokkade met ADR-013-lifecycle, het
backend opties-endpoint, en de volledige frontend-laag (login, app-shell,
Applicatie-module-view). Validatie omvat de 4 backend-assen **plus** de
frontend-poorten.

## Backend — 4 assen (CONTRIBUTING.md §6)

| As | Commando | Verwacht | Resultaat |
|----|----------|----------|-----------|
| 1 — py_compile | `find … \| xargs py_compile` | 0 syntaxfouten | **Geslaagd** — 0 fouten (alleen een `SyntaxWarning` in een overgenomen framework-skill-script, geen projectcode) |
| 2 — pytest | `python3 -m pytest backend/tests/ modules/ -q` | alle groen | **Geslaagd** — **323 passed** |
| 3 — Alembic | `alembic heads` / `branches` | 1 head, 0 branches | **Geslaagd** — 1 head `0002_platform_tenant`, 0 branches (geen nieuwe migratie deze sessie) |
| 4 — referentie-grep | grep `Eraneos\|compliman\|cm_` | 0 hits | **Geslaagd** — 0 hits (incl. `frontend/src/`, `frontend/tests/`, `.vue`) |

## Frontend — poorten

| Poort | Verwacht | Resultaat |
|-------|----------|-----------|
| `vite build` | 0 fouten | **Geslaagd** — build OK (bundle >500 kB-waarschuwing = latere code-splitting, geen fout) |
| `vitest run` | alle groen | **Geslaagd** — **38 passed** (7 bestanden) |

## Dekking deze sessie (samengevat)

- Backend: module-CRUD over 6 entiteiten (schemas `extra='forbid'` + validators;
  service tenant-scoped + cursor; routes onder `vereist_permissie`); domeinexceptie+
  handler-patroon; ADR-013 lifecycle (pure `bepaal_lifecycle` + reverse + transitie-
  gebaseerde invariant); opties-endpoint; afwijkende CRUD (Blokkade lezen+bijwerken).
- Frontend: LoginView, AppLayout (topbar/sidebar/Toast), Applicatie lijst/detail/
  formulier; rol-gating-affordance; 422/403/404/409-afhandeling; cross-root-barrels.
- **Empirische verificatie** (eenmalig, draaiende stack): login-round-trip
  (Keycloak code+PKCE) + create/list/opties bewezen — zie `docs/LOKAAL-TESTEN.md`.

## Geaccepteerde afwijkingen

- 422 = standaard FastAPI `{detail:[…]}` (geen canonieke wrapper) — bewust, OP-7.
- 401 volgt nog `{detail:{code}}` — OP-7.
- `checklist_compleet` transient (ADR-013, bewuste afwijking ADR-009).
- ADR-009 enum-voetnoten ↔ code nog niet gesynchroniseerd (code leidend).
- Frontend bundle >500 kB (DataTable) — geen fout; lazy-loading als optimalisatie.
