# TST-V011-Validatierapport

**Build**: V011
**Datum**: 2026-06-17
**Sessie**: DC010 (ADR-023 Fase F afgerond — F-3 betekenis-marker + consistentie-signalering)
**Migratie head**: `0024_adr023_vraagbetekenis`

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `py_compile` op alle Python-bestanden (excl. node_modules/.git/__pycache__/.claude) | **Geslaagd** — 0 syntaxfouten |
| 2 — Tests | `pytest backend/tests/ modules/ -q` | **Geslaagd** — 746 passed |
| 3 — Database-integriteit | `alembic heads` / `alembic branches` / RLS-count | **Geslaagd** — 1 head (`0024_adr023_vraagbetekenis`), 0 branches, 24× `ENABLE ROW LEVEL SECURITY` |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/frontend/modules/docs/adr; localStorage-token; cd_admin in app-code | **Geslaagd** — 0 hits; 0 localStorage-tokens; 4 `cd_admin`-vermeldingen zijn uitsluitend docstring/comment (geen app-runtime-verbinding) |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` | **Geslaagd** — 311 passed (42 files) |
| `vite build` | **Geslaagd** — 0 fouten (>500 kB-waarschuwing = geen fout) |

## Aantal kritieken

**0.**

## Geaccepteerde afwijkingen

- **Pre-existing env-test** `test_auth_pkce.py::test_callback_succes_zet_cd_session_cookie`:
  omgevingsgebonden (Secure-cookievlag in test/dev), DB-onafhankelijk. In de huidige omgeving **groen**.
  Staat los van de DC010-wijzigingen; niet als regressie behandeld.
- **SyntaxWarning** in `.claude/skills/engineering-team/ms365-tenant-manager/scripts/powershell_generator.py`
  (invalide escape `\S`): overgenomen framework-skill onder `.claude/`, bewust uitgesloten van de TST-scope;
  warning, geen syntaxfout.

## Invariant-borging (F-3, geverifieerd)

- **Score blijft de enige lifecycle-driver.** De betekenis-marker (`checklistvraag.betekenis`) én de
  consistentie-signalering (`plaatsingsignaal_service`) staan náást de engine: machine-geborgd via
  (a) offline import-afwezigheid (geen `lifecycle_service`/`herbereken_lifecycle`/`bepaal_lifecycle`/
  `ComponentProfiel`/`Blokkade`) + read-only bronscan (geen `session.add/commit/flush/delete`); een
  afgeleide read mág `Checklistscore`/score **lezen**; (b) live — `zet_betekenis` en het opvragen van
  signalen creëren/muteren geen `component_profiel`/`checklistscore`/lifecycle.
- **Cross-tenant datamigratie geverifieerd** (`0024`, als cd_admin): per tenant draagt exact de
  applicatie-plaatsingsvraag (`2.2`) de betekenis `technische_plaatsing`; 0 andere dragers.
- **Uniciteit** `(tenant_id, componenttype, betekenis)` afgedwongen (NULL distinct → onbeperkt NULL);
  een tweede applicatievraag dezelfde betekenis geven ⇒ 409 (live geborgd).
- **Read-only signaal-meting (dev-seed)**: 8 signalen, alle `beoordeeld_niet_vastgelegd` (plaatsing
  positief beoordeeld, geen `draait_op`-relatie). Oriëntatie `draait_op = assignment doel==component` +
  scope-via-markering (applicatieserver buiten scope) live geborgd.
- **Live-test-residu**: 0 — de live signaal-/element-tests ruimen hun `element`-rijen + relaties
  structureel op.
