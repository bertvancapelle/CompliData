# NEXT_SESSION.md — LIKARA V021

**Gegenereerd**: 2026-06-25 (sessie-afsluiting LI020)
**Build**: V020 → **V021**
**Migratie head**: `0042` (`0042_adr033_opgeslagen_view`) — geen schema-/migratiewijziging in LI020
**Tests**: frontend **654 groen (62 files)** + `vite build` ok + `test:css-build` ok; backend **890 passed / 2 skipped / 8 pre-existing live-DB-failures** (oorzaak getraceerd: test-residu — zie TST-rapport). Zie `docs/TST-V021-Validatierapport.md`.

---

## Stand van zaken (V021) — ADR-033 volledig + gebruikersbeheer-acties + Landschapskaart-reeks

Deze sessie (LI020):

- **ADR-033 (volledig)** — adaptieve Landschapskaart + Impact-verkenner als graph op het canvas;
  samenstelling-edge ("onderdeel van"); opgeslagen & deelbare views (entiteit + rechten + API + voorkant + startscherm).
- **Gebruikersbeheer-acties (ADR-029 Fase 2b, achter+voorkant)** — wachtwoord opnieuw instellen, rol wijzigen,
  in-/uitschakelen (sessie-afkap), gegevens corrigeren; self-lockout-guards; expliciete audit; beheer-paneel.
- **Landschapskaart-reeks** (frontend, engine onaangeroerd): selectie-highlight (enkelklik = incidente lijnen oranje;
  dubbelklik = dieper); organisatiestructuur-ring (persoon-met-rol → afdeling → organisatie, context, buiten impact);
  toestand-geschiedenis (terug/vooruit) + hang-fix + auto-centreren; vorm-per-type + uitklapbare legenda;
  organisatie-scopebalk slice 1 (backend read-projectie: eigenaar + gebruikt-door-orgs) + slice 2 (balk: biedt aan / gebruikt).
- **ADR-034 (swimlane-herwrite)** — vastgelegd als **Voorstel** (nog niet gebouwd).
- **Feitenchecks** — samenstelling, organisatiestructuur, eigenaar-organisatie, artefact-herkomst, seed-dekking.

---

## Top-5 prioriteiten volgende sessie (LI021) — eerste blok, in volgorde (leunt op elkaar)

1. **Test-hygiëne-fix** — de twee lekkende live-DB-tests zelf-opruimend maken via `finally`/teardown:
   `test_component_contract_op_niet_applicatie_component` (test_component_fase_b_cd052) en
   `test_score_write_driver_plus_afgeleide_delen_correlatie` (test_audit_capture_live). Breekt de
   vervuilings-cirkel; maakt de 8 falers vermoedelijk groen.
2. **Schone reset** — `docker compose down -v` → reseed → de 32 artefacten (`CD052-db-*`/`AUDIT-SRV-*`) weg.
3. **Gerichte seed-verrijking** (geen "meer data", drie ontbrekende variaties):
   - **infrastructuur** (technology-laag) onder componenten → barrel-vorm + "draait-op"/assignment-impactrelatie zichtbaar;
   - **component-samenstelling** (component↔component, onderdeel-van) → samenstelling-ring + "onderdeel-van"-impactrelatie zichtbaar;
   - **bewuste scope-gaten** — ≥1 component zonder eigenaar + ≥1 app die uitsluitend door de organisatieloze "Burgers"-groep geserved wordt → gap-tellers van de scopebalk aantoonbaar.
4. **ADR-034 swimlane-herwrite** (open subknopen) of interactieve legenda als type-filter (besproken vervolg).
5. **Codebase cleanup** (frontend/backend dode code; cytoscape-dagre opruimen) + ADR-030 contract-dekking.

Volledige backlog: `docs/OPVOLGPUNTEN.md` (sectie "Stand V021 (LI020)").

---

## Bekende risico's en aandachtspunten

- **8 pre-existing live-DB-failures** — oorzaak getraceerd (test-residu, niet-zelf-opruimende live-DB-tests);
  wordt door LI021-startpunt 1 structureel opgelost. NIET als opgelost markeren tot dan.
- Worktree is **schoon**, niets ongecommit.

---

## Geleerde patronen deze sessie

Verwerkt in de complidata-skills (frontend, tests, backend) + CONTRIBUTING.md: adaptieve één-graph-pipeline;
selectie-highlight via runtime-klassen (geen relayout); toestand-geschiedenis zonder relayout-thrash;
vorm-per-type via één gedeelde bron met luminantie-contrast; context-ringen buiten de impact-keten;
scope = scope-keuze; feitencheck-buckets vóór bouw; live-DB-tests zelf-opruimend (`finally`); één-slice-één-commit.
