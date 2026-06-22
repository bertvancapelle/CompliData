# TST-V017-Validatierapport

**Build**: V017
**Datum**: 2026-06-22
**Sessie**: DC016 (UI-standaardisatie knop/tab + interactie-borging + api-client-filterconventie; Landschapskaart popups/fullscreen; ADR-023a meervoudige flow-koppelingen Fase 1+2; skills-borging)
**Migratie head**: `0040`

## Resultaat per as (CONTRIBUTING.md sectie 6)

| As | Controle | Resultaat |
|---|---|---|
| 1 — Code-kwaliteit | `py_compile` op alle Python-bestanden (backend + modules, excl. node_modules/__pycache__) | **Geslaagd** — 0 syntaxfouten |
| 2 — Tests | `pytest backend/tests/ modules/ -q` | **Geslaagd** — **859 passed**, 1 warning |
| 3 — Database-integriteit | migratie-head / branches | **Geslaagd** — 1 head (`0040`), 0 branches; migraties deze sessie: `0039` (ADR-023a — partiële flow-uniciteit `WHERE relatietype <> 'flow'` + `naam`-kolom), `0040` (`dubbel_waarschuwing_genegeerd`-kolom). Up/down-rondtrip beide schoon geverifieerd |
| 4 — Veiligheid/conventies | grep `Eraneos\|compliman\|cm_` op backend/frontend/modules/docs-adr | **Geslaagd** — 0 hits |

## Frontend-poorten

| Poort | Resultaat |
|---|---|
| `vitest run` | **Geslaagd** — **534 passed (61 files)** |
| `vite build` | **Geslaagd** — 0 fouten |
| `npm run test:css-build` | **Geslaagd** — alle 6 kritische interactie-klassen aanwezig in de gebouwde CSS (exit 0) |

## Aantal kritieken

**0.**

## Invariant-borging (DC016, geverifieerd)

- **Score blijft de enige lifecycle-driver.** De ADR-023a-koppeling-uitbreiding staat náást de engine,
  dubbel-geborgd: `relatie_service` importeert geen `lifecycle_service`/`herbereken_lifecycle`/
  `bepaal_lifecycle`/`ComponentProfiel`/`Blokkade`/`Checklistscore` (offline import-afwezigheidstest)
  én het aanmaken van flows — inclusief de overrule — laat **geen `component_profiel`** ontstaan
  (live-test, `profielen == 0`). De dubbel-signalering en de override-markering zijn registratief,
  géén engine-poort.
- **UI-interactie-borging (drie lagen):** token-contracttest + component-render-state-test +
  build-CSS-check (`test:css-build`) — de laatste vangt een ontbrekende `@source` of een weggevallen
  kritische interactie-klasse; de-vervuild zodat de check zijn eigen klassen niet zaait (geen vals-groen).
- **Api-client-filterconventie:** snake_case + `_filterQuery`-allowlist (onbekende key = luide fout),
  geborgd door `api.filter.test.js` (filter in de URL + luide fout op onbekende key).
- **Koppeling-wederkerigheid (gevalideerd):** één gedeelde gerichte flow-rij; uitgaand bij de bron,
  inkomend bij het doel; geen heen/terug-duplicaat.

## Geaccepteerde afwijkingen

- **Pre-existing env-test/warning** (`RuntimeWarning` in een lifecycle-test-mock; pre-existing): warning,
  geen fout — staat los van de DC016-wijzigingen.
- **`test:css-build` draait nog niet in CI** (los script) — opvolgpunt (zie OPVOLGPUNTEN.md), geen
  TST-blokker.

## Dekking deze sessie

- UI-standaardisatie: knop-preset (`23ccfc8`), tabs + vaste hoogte (`55eca62`), één-hoogte/geen-size
  (`8912203`), UI-interactie-borging drie lagen (`cb4b9e7`), Tailwind `@source` voor module-views
  (`6f04ed2`).
- Landschapskaart: klik-popups (koppeling + knoop) + in-app fullscreen (`8de3451`).
- Api-client-filterconventie: snake_case + allowlist + luide fout (`9da57d0`).
- ADR-023a meervoudige flow-koppelingen: Fase 1 schema (`80f0655`, migratie 0039), Fase 2 validatie +
  dubbel-signalering + override-audit (`7a6e440`, migratie 0040).
- ADR-030 contract-dekking per band (voorstel, `3e28481` — extern geland).
- Skills-borging DC016 (`2bfcbd8`).
- Migraties deze sessie: `0039`, `0040` (beide niet-destructief; head = 0040).
