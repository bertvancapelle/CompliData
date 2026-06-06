-- CompliData database initialisatie
-- Draait eenmalig via docker-entrypoint-initdb.d bij eerste container-start.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Applicatie-rol voor de FastAPI backend (non-superuser, onderworpen aan RLS)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'cd_app') THEN
        CREATE ROLE cd_app LOGIN PASSWORD 'changeme_dev';
    END IF;
END
$$;

-- Geef cd_app toegang tot public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cd_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cd_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cd_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cd_app;

-- Platform-rol voor platform-endpoints (ADR-012): non-superuser, GEEN RLS-bypass,
-- GEEN toegang tot tenant-tabellen. Tabel-specifieke rechten op de platform-
-- tabellen (Tenant/Platforminstellingen/Platformmetadata) worden bij het
-- aanmaken van die tabellen gegrant (aparte migratie). Hier alleen de rol +
-- schema-USAGE; bewust GEEN ALTER DEFAULT PRIVILEGES (least privilege).
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'cd_platform') THEN
        CREATE ROLE cd_platform LOGIN PASSWORD 'changeme_dev';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO cd_platform;

-- Row Level Security vereist dat deze session-variabele door de applicatie
-- vóór elke transactie wordt gezet:
--   SELECT set_config('app.tenant_id', '<uuid>', false);
-- Ontbreekt de variabele, dan weigert elke RLS-policy alle rijen.
-- FORCE zorgt dat RLS ook geldt voor table-owners.
