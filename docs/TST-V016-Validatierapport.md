# TST-V016-Validatierapport

**Build**: V016
**Datum**: 2026-06-20
**Sessie**: DC015 (ADR-029 gebruikersbeheer als primaire ingang — Fase 2/4/3b/3a + objecthistorie; + dev-seed-fix)
**Migratie head**: `0038`

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `py_compile` op alle Python-bestanden (backend + modules, excl. node_modules/__pycache__) | **Geslaagd** — 0 syntaxfouten |
| 2 — Tests | `pytest backend/tests/ modules/ -q` | **Geslaagd** — **856 passed**, 1 warning |
| 3 — Database-integriteit | migratie-head / RLS-policies | **Geslaagd** — 1 head (`0038`), 0 branches; RLS present incl. nieuwe `gebruiker_persoon` (`relrowsecurity=t`, `relforcerowsecurity=t`); migraties deze sessie: `0037` (gebruiker_persoon), `0038` (klaarverklaring `verklaard_door_sub`) |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/frontend/modules; localStorage-token; cd_admin runtime-verbinding | **Geslaagd** — 0 hits; 0 localStorage-tokens; 0 cd_admin in app-runtime-code (4 `cd_admin`-DSN's zijn uitsluitend test-fixtures onder `modules/.../tests/`, pre-existing patroon) |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` | **Geslaagd** — **500 passed (57 files)** |
| `vite build` | **Geslaagd** — 0 fouten |

## Aantal kritieken

**0.**

## Invariant-borging (DC015, geverifieerd)

- **Score blijft de enige lifecycle-driver.** Elke nieuwe schakel staat náást de engine, machine-geborgd:
  1. **gebruiker_service** (Fase 2): offline import-afwezigheidstest (geen `lifecycle_service`/
     `herbereken_lifecycle`/`bepaal_lifecycle`/`ComponentProfiel`/`Blokkade`/`Checklistscore`) +
     live geen-mutatie (gebruikersaanmaak raakt de component-lifecycle niet).
  2. **actor_resolutie** (Fase 3b): engine-import-afwezigheid; read-only naam-lookup. Live
     geen-mutatie bij klaarverklaring (statuswissel raakt `lifecycle_status` niet).
  3. **auditlog_service / objecthistorie** (Fase 3a + objecthistorie): read-only; de objecthistorie-
     route importeert geen engine-symbolen (import-afwezigheidstest).
- **Toegang-volgt-object** is read-only autorisatie: object eerst resolveren (`*_service.haal_op` →
  404 no-leak), dan de leespermissie van het objecttype — geen AUDITLOG-gate, geen mutatie.

## Geaccepteerde afwijkingen

- **Pre-existing env-test** `test_auth_pkce.py` (Secure-cookievlag, omgevingsgebonden): in deze omgeving
  groen; staat los van de DC015-wijzigingen.
- **SyntaxWarning** in een overgenomen framework-skill onder `.claude/` (buiten TST-scope; warning, geen fout).
- **4 cd_admin-DSN's** in test-fixtures (`modules/.../tests/`): legitiem (test-setup/seed), geen app-runtime-verbinding.

## Dekking deze sessie

- ADR-029 Fase 2 (gebruiker_persoon + KC-provisioning service-account, migratie 0037),
  Fase 4 (gebruikersbeheer-scherm), Fase 3b (sub-stempeling klaarverklaring/plateau +
  `actor_resolutie`, migratie 0038), Fase 3a (audit-view + naam/actie-filter), objecthistorie
  ('i'-knop op 8 schermen). Commits: 572aa4c (dev-seed-fix), 0e6035b, c227e7a, 2ab091d, fea3768, a4fd048.
- Migraties deze sessie: `0037`, `0038` (beide niet-destructief toegepast op dev-DB; head = 0038).
