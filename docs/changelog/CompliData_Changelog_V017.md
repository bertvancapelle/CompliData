# CompliData Changelog V017

**Datum**: 2026-06-22
**Sessie**: DC016
**Migratie head**: `0040`

## Wijzigingen

### UI-standaardisatie & interactie-borging
- `23ccfc8` — knop-preset gestandaardiseerd (ghost-variant + lichtblauwe secondary).
- `55eca62` — tabbladen knop-consistent + vaste knophoogte + subsectie-acties secondary.
- `8912203` — knopstandaard: één vaste hoogte (`h-10`), geen size-variatie.
- `cb4b9e7` — UI-interactiestates-borging: token-contract + render-state + build-CSS-check.
- `6f04ed2` — Tailwind `@source` voor module-views (tab-hover compileert weer).

### Landschapskaart
- `8de3451` — klik-popups (koppeling + knoop) + in-app fullscreen-overlay.

### Api-client
- `9da57d0` — api-client filterconventie: snake_case + allowlist (luide fout op onbekende key).

### ADR-023a — meervoudige flow-koppelingen
- `80f0655` — Fase 1: partiële flow-uniciteit (`WHERE relatietype <> 'flow'`) + `naam`-kolom (migratie 0039).
- `7a6e440` — Fase 2: naam-verplicht-flow + overrulebare KOPPELING_DUBBEL-signalering + override-audit (migratie 0040).

### Architectuur / docs
- `3e28481` — ADR-030 contract-dekking per contract↔component-band (voorstel; extern geland).
- `2bfcbd8` — DC016 skills-borging stap 1 (knop/tab/UI-borging/api-filter/ADR-023a/testdata/sessiebewaking).

### Validatie
- Backend **859** + frontend **534** groen; `test:css-build` groen; migratie head `0040` (1 head, 0 branches).
