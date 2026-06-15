# CompliData Changelog V009

**Datum**: 2026-06-14

## Wijzigingen

### ADR-006 audit-trail (#17) — VOLLEDIG af + GELAND (commit `6eb0699`)

Migratie 0010: `audit_log` (tenant-scoped) + `platform_audit_log`, FORCE RLS, append-only grant +
`REVOKE ALL` + `BEFORE UPDATE/DELETE/TRUNCATE`-trigger. Capture-hook (`before`/`after_flush`, ORM-only),
actor via ContextVar + `system:dev_seed`/`platform_init`, per-tenant SHA-256 hash-keten met
`pg_advisory_xact_lock`-serialisatie (fork uitgesloten), blokkade-classificatie gesplitst
`derive`/`update`, lees-API `GET /auditlog` + RBAC `AUDITLOG`, capture-grens-invariant.

### ADR-023 (ArchiMate-uitlijning) — CUTOVER (Fase A + B) AF + GELAND (commit `038f100`, 57 bestanden, live-geverifieerd op verse DB)

Migratieketen t/m **0017**:

- **Fase A (0011)**: element-supertabel (shared-PK, `UNIQUE(tenant_id,id)`, FORCE RLS) +
  ArchiMate-typing-catalogus (`archimate_element`/`laag`/`aspect` op `componentconfig_optie`) +
  dimensie `archimate_relatie` (8 typen: composition/aggregation/serving/assignment/flow/realization/
  association/access) + per-type kenmerk-definities.
- **Fase B-core (0012)**: één getypeerd relatiemodel (composiet-FK bron/doel → element, kenmerken jsonb,
  UNIQUE, CHECK bron≠doel, FORCE RLS) + service + RBAC `RELATIE` + audit-allowlist.
- **B-mig-1 (0013)**: element-promotie datatype/gebruikersgroep/contract (additief).
- **Cutover slices (0014–0017)**: koppeling→flow (richting/protocol/impact als kenmerken, 1-op-1,
  tweerichting als kenmerk); component_structuur→assignment (host→gehoste, oriëntatie omgedraaid)/
  aggregation; component_contract→association (rol als kenmerk); datatype/gebruikersgroep-band→
  access/serving + drop `applicatie_id` + CASCADE-wijziging (Besluit 13) + wees-detectie. Oude tabellen
  gedropt; impact-graaf type-bewust herbouwd op het relatiemodel.
- **Twee mechanische live-stop-fixes meegegaan**: revisie-ID 0016 ingekort (<32 tekens, `alembic_version`
  `varchar(32)`); `seed_componentconfig` uniforme dict-keys voor multi-row insert (waarden byte-identiek).

### Migraties

Head **0017** (`0017_adr023_cutover_band`).

### Teststatus

Backend 651 passed / 1 pre-existing env-test (`test_auth_pkce` Secure-cookie, DB-onafhankelijk, los van
ADR-023); frontend 255 passed.

### Open (ADR-023, volgende sessies)

- **Fase C**: technologielaag (node/system_software eersteklas).
- **Fase D**: contract-element-verfijning + dekking.
- **Fase E**: migratielaag (plateau/gap/work_package/deliverable) + checklist-consistentiecheck
  technische plaatsing.
- **Fase F**: gelaagde ArchiMate-lees-API + gap/plateau-view + migratie-UI + RBAC nieuwe entiteiten +
  audit-allowlist.
- **Fase G** (export): buiten scope.

### Follow-ups (Fase F / opruim)

- (a) live-test-teardowns ruimen de element-supertype-rij niet op (11 testresidu-elementen; `down -v`
  wist het; productiecode correct via element-cascade);
- (b) migratie-ID-lengteconventie ≤32 tekens;
- (c) dode `KoppelingConflict`-refs + checklistconfig stray docstring.
