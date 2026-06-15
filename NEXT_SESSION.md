# NEXT_SESSION.md — CompliData V009

**Gegenereerd**: 2026-06-14
**Vorige build (deze afsluiting)**: V008 → **V009**
**Laatste commits vóór de bump**: `6eb0699` (ADR-006 audit-trail) → `038f100` (ADR-023 cutover)

---

## Stand van zaken (V009)

Twee volledig afgeronde + gelande architectuurtrajecten bovenop V008:

- **ADR-006 audit-trail (#17)** (`6eb0699`, migratie `0010`): append-only `audit_log` (tenant) +
  `platform_audit_log`, FORCE RLS, `REVOKE ALL` + `BEFORE UPDATE/DELETE/TRUNCATE`-trigger,
  capture-hook (`before/after_flush`, ORM-only), actor via ContextVar, per-tenant SHA-256 hash-keten
  met `pg_advisory_xact_lock`-serialisatie, lees-API `GET /auditlog` + RBAC `AUDITLOG`.
- **ADR-023 ArchiMate-cutover (Fase A + B)** (`038f100`, 57 bestanden, live-geverifieerd, migratie
  t/m `0017`): element-supertype (shared-PK) + ArchiMate-typing-catalogus; één getypeerd `relatie`-model;
  element-promotie datatype/gebruikersgroep/contract; cutover koppeling→flow, component_structuur→
  assignment/aggregation, component_contract→association, datatype/gebruikersgroep-band→access/serving
  (drop `applicatie_id`, CASCADE-wijziging Besluit 13, wees-detectie). Oude tabellen gedropt.
- **651** backend (1 pre-existing env-test) + **255** frontend groen. Migratie head `0017`.

---

## Top-5 prioriteiten volgende sessie

1. **ADR-023 Fase C — technologielaag eersteklas** (node/system_software): database/applicatieserver/
   middleware/fileshare als volwaardige technology-laag-elementen met juiste mapping/relaties. Start hier.
2. **ADR-023 Fase D** — contract-element-verfijning + dekkingstests rond de association-relatie.
3. **ADR-023 Fase E** — migratielaag (plateau/gap/work_package/deliverable) + checklist-consistentiecheck
   technische plaatsing.
4. **ADR-023 Fase F** — gelaagde ArchiMate-lees-API + gap/plateau-view + migratie-UI + RBAC nieuwe
   entiteiten + audit-allowlist; opruim-follow-ups (a/b/c) meenemen. Fase G (export) buiten scope.
5. **Opruim** — dode `KoppelingConflict`-refs + checklistconfig stray docstring (follow-up c);
   live-test-teardown-residu structureel (follow-up a).

---

## Bekende risico's en aandachtspunten

- **Na een `down -v`-reset opnieuw inloggen in de UI** — verlopen sessie (Redis/Keycloak-DB leeg),
  géén bug.
- **Live-test-teardown-residu**: integratietests laten 11 `element`-supertype-rijen achter (subtype +
  relatie wél opgeruimd). Productiecode correct (element-cascade). `down -v` wist het.

---

## Technische schuld

- (a) Live-test-teardowns ruimen de in ADR-023 nieuwe `element`-supertabel niet op.
- (b) Migratie-revisie-ID-conventie: ≤32 tekens (`alembic_version` is `varchar(32)`).
- (c) Dode `KoppelingConflict`-referenties + checklistconfig stray docstring.
- Pre-existing env-test `test_auth_pkce::…secure…` (cookie `Secure`-vlag in dev/test; DB-onafhankelijk).

---

## Uitgestelde punten (achtergrond)

Zie `docs/OPVOLGPUNTEN.md`: OP-3 (refresh-token), OP-13 (platform-tabel-grants), OP-14 (secrets),
OP-21, OP-23, OP-24, OP-25, OP-26, OP-27, OP-28 (VPS), OP-29 (impact-lens label), OP-30 (auth-cookie env-test).

---

## Geleerde patronen deze sessie

- **Big-bang cutover in reviewbare slices** + één verplichte live-stop met DB-reset: elke slice
  offline-groen, daarna één keer live verifiëren (datamigratie-equivalentie + richting, RLS/composiet-FK,
  append-only audit).
- **Verse-DB-verificatie legde twee mechanische defecten bloot** die offline onzichtbaar waren:
  revisie-ID > `varchar(32)` en een multi-row `pg_insert` met niet-uniforme dict-keys.

---

## Werkwijze (triggerdiscipline)

Elke opdracht-`.md` begint op **regel 1** met `START: [taaknaam]`. **`AKKOORD: commit`** is exclusief
de commit-trigger op een groen eindrapport. CC verifieert zélf de groene staat vóór elke commit. Dev:
`cd-api` draait met `--reload`. Reset-procedure: `docs/LOKAAL-TESTEN.md`. Startpunt volgende sessie:
`docs/_output/CompliData_Sessiestart_V009.zip` → **ADR-023 Fase C**.
