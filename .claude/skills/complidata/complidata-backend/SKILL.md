---
name: complidata-backend
description: Backend-patronen voor CompliData (FastAPI + SQLAlchemy + Alembic). Beschrijft de werkelijke V001-staat.
stack: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy asyncio, Alembic, PostgreSQL 16
bijgewerkt: V001
---

# CompliData Backend Skill

## App-factory en lifespan

```python
# backend/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_startup_config()  # faalt leesbaar bij ontbrekende env-vars
    yield

app = FastAPI(
    title="CompliData API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
```

## Middleware-volgorde (buitenste eerst)

```python
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(OriginCheckMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

## Router-registratie

```python
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
# Module-routers hier toevoegen, bijv.:
# app.include_router(bwb_router, prefix="/api/v1")
```

## Database-sessies

| Functie | Gebruik |
|---|---|
| `get_session(tenant_id)` | Tenant-scoped (RLS-context gezet) |
| `get_worker_session(tenant_id)` | Achtergrond-workers (verse sessie per event) |
| `get_platform_db_session()` | Platform-brede queries (geen RLS-context) |

RLS-context — ALTIJD via `set_config`, NOOIT via `SET`:

```python
await session.execute(
    text("SELECT set_config('app.tenant_id', :tid, false)"),
    {"tid": str(tenant_id)},
)
```

## Config-regels

- Pydantic-settings met `extra="ignore"`.
- Verplichte velden zonder default: `database_url`, `database_url_sync`,
  `admin_database_url`, `keycloak_url/realm/client_id/client_secret`,
  `rabbitmq_url` — de app start niet zonder deze (`validate_startup_config`).
- Cookie-naam: `cd_session`.
- Test-mode: `COMPLIDATA_TEST_MODE=true` versoepelt Origin-check en
  rate-limit-key.

## Enum-sync-patroon (Python ↔ PostgreSQL)

LET OP: de generieke `sa.Enum` accepteert **geen** `create_type`-parameter
(dat geeft een TypeError bij import). De enum-DDL wordt volledig door de
Alembic-migratie beheerd; het model verwijst alleen naar de type-naam.

```python
# Python enum
class HostingModel(str, Enum):
    saas = "saas"
    on_premise = "on_premise"

# Model-kolomtype — generieke sa.Enum, GEEN create_type, naam eindigt op _enum
hostingmodel_enum = sa.Enum(HostingModel, name="hostingmodel_enum")

# Gedeeld type-object voor hergebruik over meerdere kolommen
niveau_enum = sa.Enum(NiveauEnum, name="niveau_enum")  # complexiteit + prioriteit
```

In de **migratie** (niet in het model) wordt `postgresql.ENUM(..., create_type=False)`
gebruikt en expliciet `.create(bind, checkfirst=True)` aangeroepen — zie de
complidata-db skill.

## Model-patroon

```python
class Applicatie(Base, TenantMixin, TimestampMixin):
    __tablename__ = "applicatie"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    naam: Mapped[str] = mapped_column(String(255), nullable=False)
    hostingmodel: Mapped[HostingModel] = mapped_column(hostingmodel_enum, nullable=False)
    # Configureerbaar per tenant — bewust vrije tekst, geen hardcoded enum
    eigenaar_organisatie: Mapped[str] = mapped_column(String(120), nullable=False)
```

`Base`, `TenantMixin`, `TimestampMixin` komen uit `app.models.base`.

## Seed-patroon (idempotent)

```python
async def seed_checklist_vragen(session) -> int:
    rows = [{**v, "prioriteit": ChecklistPrioriteit(v["prioriteit"])}
            for v in CHECKLIST_VRAGEN]
    stmt = pg_insert(ChecklistVraag).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["code"])
    await session.execute(stmt)
    await session.commit()
    return len(CHECKLIST_VRAGEN)   # vast 89, ook bij idempotente herhaling
```

Gebruik `len(...)` als returnwaarde — `result.rowcount` zou bij een tweede
(idempotente) run 0 teruggeven.

## Stubs en openstaande ADRs (V001)

| Onderdeel | Status |
|---|---|
| `_load_roles()` | Stub — geeft `[]` — RBAC volgt uit ADR-010 |
| `AuthenticatedUser.roles` | Altijd leeg tot ADR-010 |
| Rate-limit-decorators op endpoints | Nog niet toegepast (limiter wel geregistreerd) |
| Audit/hash-chaining | Niet geïmplementeerd — ADR-006 open |
