# ADR-011 — Deploy- en migratiestrategie: aparte init-container

| | |
|---|---|
| **Status** | Aanvaard |
| **Datum** | 2026-06-06 |
| **Beslissers** | Bert van Capelle (G. van Capelle Beheer B.V.) |
| **Gerelateerd** | ADR-001 (platform-architectuur), ADR-003 (multi-tenant RLS), ADR-002 (IAM) |

## Context

De applicatie verbindt met de database als `cd_app` — een non-superuser die
onderworpen is aan Row Level Security (RLS). Uit de eerste live DB-run (P4)
bleek concreet:

- `cd_app` heeft **geen `CREATE` op schema `public`**
  (`has_schema_privilege('cd_app','public','CREATE') = false`); `cd_app` kan
  dus geen tabellen/enums aanmaken en kan `alembic upgrade head` niet draaien.
- `cd_admin` is superuser/owner en voert de DDL uit; door
  `FORCE ROW LEVEL SECURITY` geldt tenant-isolatie ook voor de owner, maar
  superuser-DDL is nodig om het schema te bouwen.
- De referentiedata (89 checklistvragen, ADR-009) wordt na de migratie
  geseed via `platform_init` (idempotent, `ON CONFLICT DO NOTHING`).

We moeten vastleggen **hoe** migratie + platform-seed in een deployment
draaien, met behoud van de harde regel dat `cd_admin` **nooit** in de
applicatielaag voorkomt (omzeilt RLS).

## Besluit

### B1 — Aparte init-container (`cd-migrate`)

Migratie en platform-seed draaien in een **aparte, kortlevende
init-container** die hetzelfde image gebruikt als de API, maar:

1. verbindt als **`cd_admin`** (eigen DB-URL);
2. uitvoert: `alembic upgrade head` → `python3 -m app.platform_init`;
3. **run-to-completion** afsluit (geen langdraaiend proces).

### B2 — Gating vóór de app-container

`cd-api` start pas na succesvolle afronding van de init-container:

```yaml
depends_on:
  postgres: { condition: service_healthy }
  cd-migrate: { condition: service_completed_successfully }
```

Faalt de migratie/seed, dan start de app niet — fail-fast op deployniveau.

### B3 — Rechtenscheiding blijft hard

- `cd_admin` komt **uitsluitend** in de init-container voor.
- De **app-container houdt uitsluitend `cd_app`**; geen admin-credential in
  de applicatielaag (conform CLAUDE.md / ADR-003).
- `platform_init` is onderdeel van de init-container, **niet** van de
  app-entrypoint (die blijft `uvicorn`).

## Gevolgen

- **Operationeel**: één deterministische volgorde — DB healthy → migrate+seed
  (cd_admin) → app (cd_app). Een verse `docker compose up` levert een volledig
  geïnitialiseerde stack zonder handmatige stappen.
- **Security**: het admin-credential heeft een minimaal blootstellingsvlak
  (alleen de init-container, die direct afsluit); de langdraaiende app draait
  rechtenarm als `cd_app` onder RLS.
- **Idempotentie**: herhaalde runs zijn veilig (Alembic is versie-gestuurd;
  `platform_init` gebruikt `ON CONFLICT DO NOTHING`).
- **Lokaal/CI alternatief**: dezelfde twee commando's kunnen handmatig
  (`alembic upgrade head` als cd_admin, daarna `python3 -m app.platform_init`)
  worden gedraaid; de container-flow is leidend voor deployments.

## Alternatieven overwogen

- **Handmatige/CI-stap** (operator draait migratie buiten de stack):
  verworpen als primaire flow — foutgevoelig, niet reproduceerbaar bij een
  kale `docker compose up`, en niet afdwingbaar vóór app-start.
- **App-entrypoint migreert zelf** (`alembic` in de api-entrypoint):
  verworpen — de app-container draait als `cd_app` zonder `CREATE`, dus de
  migratie zou falen; bovendien zou dit een admin-credential of een
  rolwissel in de app-laag vergen (schending van de rechtenscheiding).
- **App-container met twee credentials** (cd_admin voor migratie, cd_app voor
  runtime): verworpen — `cd_admin` in de app-laag is expliciet verboden
  (omzeilt RLS); de blootstelling is onaanvaardbaar voor een langdraaiend
  proces.
