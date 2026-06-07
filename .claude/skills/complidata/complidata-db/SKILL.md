---
name: complidata-db
description: Database-patronen voor CompliData (PostgreSQL 16, RLS, Alembic). Beschrijft de werkelijke V001-staat.
stack: PostgreSQL 16, SQLAlchemy asyncio, Alembic
bijgewerkt: V003
---

# CompliData Database Skill

## RLS-boilerplate (elke nieuwe tenant-tabel)

```sql
ALTER TABLE {tabel} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {tabel} FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON {tabel}
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
GRANT SELECT, INSERT, UPDATE, DELETE ON {tabel} TO cd_app;
```

`FORCE` is verplicht — zonder FORCE omzeilen table-owners de policy.

## GRANT-patroon

```sql
-- Tenant-tabel
GRANT SELECT, INSERT, UPDATE, DELETE ON {tabel} TO cd_app;

-- Referentietabel (geen RLS) — inclusief sequence voor de int-PK
GRANT SELECT, INSERT, UPDATE ON checklistvraag TO cd_app;
GRANT USAGE, SELECT ON SEQUENCE checklistvraag_id_seq TO cd_app;
```

## PostgreSQL enum-types in migraties

In de migratie (niet in het model) worden enum-types expliciet aangemaakt.
`postgresql.ENUM` accepteert wél `create_type=False`; de aanmaak gebeurt via
`.create(bind, checkfirst=True)`. Type-namen eindigen op `_enum`.

```python
# upgrade
hostingmodel = postgresql.ENUM(
    "on_premise", "private_cloud", "saas", "iaas", "paas", "hybride", "onbekend",
    name="hostingmodel_enum", create_type=False,
)
hostingmodel.create(op.get_bind(), checkfirst=True)
# ... daarna in create_table: sa.Column("hostingmodel", hostingmodel, ...)

# downgrade
postgresql.ENUM(name="hostingmodel_enum").drop(op.get_bind(), checkfirst=True)
```

## Index-strategie

```python
op.create_index("ix_applicatie_tenant", "applicatie", ["tenant_id"])
op.create_index("ix_applicatie_tenant_lifecycle", "applicatie",
                ["tenant_id", "lifecycle_status"])
op.create_index("ix_koppeling_tenant_bron", "koppeling",
                ["tenant_id", "bron_applicatie_id"])
```

Plaats `tenant_id` als eerste kolom in composite indexen.

## FK-volgorde en CASCADE

- Create-volgorde: ouder-tabel vóór kind-tabel (FK's resolven).
- `ON DELETE CASCADE` op kind-FK's binnen tenant-scope.
- `CHECK bron_applicatie_id <> doel_applicatie_id` op Koppeling.
- `UNIQUE (tenant_id, applicatie_id, vraag_code)` op Checklistscore.
- Drop-volgorde in downgrade: omgekeerd (kind vóór ouder).

## Referentietabel-uitzondering

`ChecklistVraag` heeft **geen** RLS en **geen** `tenant_id` — het is
platform-brede seeddata die alle tenants delen (int-PK, `code` UNIQUE).
Alleen `GRANT SELECT, INSERT, UPDATE` + sequence-grant voor `cd_app`.

## Alembic multi-location (platform + modules)

```ini
# backend/alembic.ini — separator is ":" (os.pathsep op posix)
version_locations = %(here)s/alembic/versions:%(here)s/../modules/bwb_ontvlechting/migrations/versions
```

Module-migratie: `down_revision = None` (root, want de platform-versions
zijn leeg in V001). Verificatie offline: `alembic heads`, `alembic history`,
`alembic upgrade head --sql`.

## DB-rollen — driedeling (ADR-011/012, least privilege)

| Rol | Type | Waar | Gebruik |
|---|---|---|---|
| `cd_admin` | superuser | **uitsluitend** de init-container | migratie (`alembic upgrade head`) + `platform_init`. NOOIT in de app-runtime. |
| `cd_platform` | non-superuser | app-laag | platform-endpoints (tenant-provisioning, platforminstellingen). Grants **per platform-tabel** (least privilege), GEEN `CREATE`/DDL, GEEN toegang tot tenant-tabellen. |
| `cd_app` | non-superuser | app-laag | tenant-werk onder RLS. |

- Migreren als `cd_app` **kan niet en mag niet**: `cd_app` heeft geen `CREATE`
  op schema `public` (`has_schema_privilege('cd_app','public','CREATE')=false`),
  dus DDL faalt; bovendien hoort migratie als `cd_admin` (superuser/owner).
- `cd_platform` (init-db): `CREATE ROLE cd_platform LOGIN` + `GRANT USAGE ON
  SCHEMA public` — bewust **geen** `ALTER DEFAULT PRIVILEGES`. Per platform-tabel
  in de migratie: `GRANT SELECT,INSERT,UPDATE,DELETE ON {tabel} TO cd_platform`
  én `REVOKE ALL ON {tabel} FROM cd_app` (platform-register valt buiten het
  tenant-domein). Verificatie: cd_platform op een tenant-/referentietabel →
  `permission denied`.

## Migratie + platform-seed (init-container, ADR-011)

```yaml
# docker-compose.yml — cd-migrate draait als cd_admin, run-to-completion
migrate:
  image: complidata-api:local
  command: ["sh","-c","python3 -m alembic upgrade head && python3 -m app.platform_init"]
  # DATABASE_URL(_SYNC) = cd_admin; ook ./modules gemount (seed-bron)
api:
  depends_on:
    migrate: { condition: service_completed_successfully }   # gating vóór app-start
```

- App-entrypoint blijft **alleen** `uvicorn` (geen migratie/seed in de app).
- `platform_init` zaait de 89 platform-brede checklistvragen (referentiedata,
  idempotent `ON CONFLICT DO NOTHING`); zie complidata-backend seed-patroon.
- Alembic multi-head vermijden: platform-migraties in
  `backend/alembic/versions/` ketenen aan de module-head (`down_revision`),
  zodat `alembic heads` = 1 blijft.

## Naamgeving

- Platform-prefix: `cd_` (database `complidata`, rollen, containers `cd-*`).
- App-gebruiker: `cd_app` (non-superuser — omzeilt RLS NIET).
- Platform-gebruiker: `cd_platform` (non-superuser — platform-endpoints, ADR-012).
- Admin-gebruiker: `cd_admin` — superuser, UITSLUITEND in de init-container.
- Enum-typenamen: lowercase snake_case eindigend op `_enum`
  (`hostingmodel_enum`, `lifecycle_status_enum`, `niveau_enum`).

## Enum = single source in `models.py` (V003)

De Python-enums in `modules/bwb_ontvlechting/backend/models/models.py` zijn de
bron; de migratie spiegelt exact dezelfde waarden. ADR-009-voetnoten ("voorgesteld")
zijn niet leidend — **de code is leidend**: `hostingmodel` = **7** waarden,
`migratiepad` = **6** (incl. `tijdelijk_gedeeld`), `protocol` = enum (`Koppelprotocol`).
`checklist_score`-kolom is nullable in de DB; het Create-schema dwingt non-null af
(ADR-013). ADR-009-tekst ↔ code synchroniseren staat open.

## Lifecycle-herberekening (ADR-013, Model A)

- Eén deterministische afleiding: pure `bepaal_lifecycle(huidige, aantal_gescoord,
  aantal_vragen, aantal_open_blokkades)` (DB-vrij testbaar) + tenant-scoped
  `herbereken_lifecycle(session, tenant_id, applicatie_id)` (telt vragen/scores/open
  blokkades, zet de status op het in-sessie object; caller commit). Draait na elke
  Checklistscore-/Blokkade-mutatie én na `start-inventarisatie`.
- Regel: `concept`→`concept` (enige niet-afgeleide vloer; nooit terug naar concept);
  niet-alles-gescoord → `in_inventarisatie`; alles gescoord + ≥1 open blokkade
  (`open`/`in_behandeling`) → `geblokkeerd`; anders → `migratieklaar`. Reverse mag.
- **Transitie-gebaseerde** auto-blokkade-invariant: alleen handelen als de score de
  blokkerende grens kruist (`ja/nvt ↔ nee/deels`); een ongewijzigde of
  binnen-blokkerende score laat een (handmatig) opgeloste blokkade met rust →
  "nee + opgelost" is een stabiele eindtoestand. `checklist_compleet` is **transient**
  (enum blijft, status wordt nooit gezet).

## Keyset-cursor-paginering

Opaque base64-cursor van `created_at|id`; ORDER BY `(created_at, id)`,
`WHERE (created_at, id) > (cursor)` via `sqlalchemy.tuple_`, `limit+1`-detectie.
Misvormde cursor → `ValueError` → route geeft **400 `ONGELDIGE_CURSOR`**.
Helper: `modules/bwb_ontvlechting/backend/services/pagination.py`.
