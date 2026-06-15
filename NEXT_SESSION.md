# NEXT_SESSION.md — CompliData V010

**Gegenereerd**: 2026-06-15 (sessie DC009)
**Build**: V009 → **V010**
**Laatste commit vóór de afsluiting**: `2dc38aa` (ADR-023 Fase E E3 — Deliverable)
**Migratie head**: `0021_adr023_deliverable`
**Tests**: 692 backend + 258 frontend groen (1 pre-existing, omgevingsgebonden env-test)

---

## Stand van zaken (V010)

ADR-023 grotendeels geland; **migratielaag (Fase E) is op één slice na klaar**:

- **Fase C** (`a20c74e`) — technologielaag: laag-filter/-labels + draait-op-aanmaak via `/relaties`.
- **Fase D** (`e683976`) — leverancier-onderscheid + ArchiMate-laag-borging (element-typing + dekkingstest).
- **Fase E E1** (`4a20572`) — Plateau + lidmaatschap (aggregation, dispositie + contractuele bevestiging)
  + nieuwe relatie-kenmerk-catalogus.
- **Opruim** (`21597ef`) — `relatie_rol` verhuisd naar de relatie-kenmerk-catalogus.
- **Fase E E2** (`8adb32e`) — Work Package + hiërarchie (composiet self-FK RESTRICT, cycluspreventie).
- **Fase E E3** (`2dc38aa`) — Deliverable + realisatieketen (work_package → deliverable → plateau via
  `realization`).

Score blijft de enige lifecycle-driver — engine onaangeroerd, dubbel geborgd (offline import-afwezigheid
+ live geen-profiel). Skills (db/backend/tests) bijgewerkt naar V010 met de 4 canonieke patronen.

---

## Top-5 prioriteiten volgende sessie

1. **ADR-023 Fase E — E4 (Gap + readiness-rollup)** — de afsluitende migratielaag-slice. Gap = element-
   subtype met **vaste 2-ariteit** baseline/doel-plateau (FK-kolommen, géén relatie — uitzondering op de
   facade-conventie). **Readiness = ROLLUP** puur read-only uit de bestaande lifecycle (geen tweede bron;
   alleen checklist-dragende leden tellen mee). **Schema-rakend → gate** vóór commit. Start hier.
2. **ADR-023 Fase F** — gelaagde ArchiMate-lees-API + gap/plateau-/migratie-views (frontend) +
   **E-8 checklist-consistentiecheck** (read-only signalering: antwoord-ja ↔ draait_op-relatie) +
   RBAC/audit-afronding. Open Exchange-export blijft buiten scope.
3. **Latente `applicatie.checklist_dragend`-drift oplossen** (OPVOLGPUNTEN #2) — vóór code de vlag voor
   `applicatie` gaat vertrouwen (aannemelijk in Fase E/F): seed ↔ migratie 0009 in lijn brengen.
4. **Platform-beheerscherm relatie-kenmerk-catalogus** (OPVOLGPUNTEN #1) — `dispositie`/`relatie_rol`
   beheerbaar maken (nu alleen geseed). Fase-F-werk.
5. **checklist-dragend als beheerder-functie** (OPVOLGPUNTEN #3) — productkeuze + type-specifieke vragen;
   Fase F / onboarding.

---

## Bekende risico's en aandachtspunten

- **Na een `down -v`-reset opnieuw inloggen in de UI** (verlopen sessie) — géén bug.
- **`applicatie.checklist_dragend=false` in de catalogus** terwijl applicaties wél checklist-dragend zijn
  (hardgecodeerd pad). De vlag is niet betrouwbaar voor `applicatie` — zie OPVOLGPUNTEN #2.
- **Pre-existing env-test** `test_auth_pkce` (Secure-cookie, DB-onafhankelijk) — omgevingsgebonden.

---

## Werkwijze (triggerdiscipline)

Elke opdracht-`.md` begint op **regel 1** met `START: [taaknaam]`. **`AKKOORD: commit`** is exclusief de
commit-trigger op een groen (gate-)rapport. Schema-rakende slices = **gate** vóór commit; licht/additief
= doorloop. CC verifieert zélf de groene staat vóór elke commit. Reset-procedure: `docs/LOKAAL-TESTEN.md`.
Startpunt volgende sessie: `docs/_output/CompliData_Sessiestart_V010.zip` → **ADR-023 Fase E (E4 — Gap)**.
