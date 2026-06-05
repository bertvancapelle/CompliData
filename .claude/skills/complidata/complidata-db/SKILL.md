---
name: complidata-db
description: Database-patronen voor CompliData (PostgreSQL 16, RLS, Alembic). Beschrijft de werkelijke V001-staat.
stack: PostgreSQL 16, SQLAlchemy asyncio, Alembic
bijgewerkt: V001
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

## Naamgeving

- Platform-prefix: `cd_` (database `complidata`, rollen, containers `cd-*`).
- App-gebruiker: `cd_app` (non-superuser — omzeilt RLS NIET).
- Admin-gebruiker: `cd_admin` — NOOIT in applicatie-schrijfpaden.
- Enum-typenamen: lowercase snake_case eindigend op `_enum`
  (`hostingmodel_enum`, `lifecycle_status_enum`, `niveau_enum`).
