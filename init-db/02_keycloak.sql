-- CompliData — Keycloak eigen database (CD055, A1).
--
-- Isoleert Keycloak's interne schema (o.a. zijn eigen COMPONENT-tabel) van de
-- app-database complidata/public. Lost de table-name-collision op die Keycloak
-- belette te starten en houdt Keycloak-schema/credentials uit de complidata-dump
-- (sluit OP-22). Draait eenmalig via docker-entrypoint-initdb.d bij lege data-dir,
-- als de superuser (cd_admin), verbonden met de default-DB complidata.

-- Eigen, least-privilege rol: eigenaar van uitsluitend de keycloak-DB. Geen
-- hergebruik van cd_admin. Dev-wachtwoord conform cd_app/cd_platform (changeme_dev).
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'kc_user') THEN
        CREATE ROLE kc_user LOGIN PASSWORD 'changeme_dev';
    END IF;
END
$$;

-- CREATE DATABASE kan niet in een transactie/DO-blok; conditioneel via \gexec.
SELECT 'CREATE DATABASE keycloak OWNER kc_user'
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak')\gexec

-- Keycloak (kc_user) beheert zijn eigen schema. In PostgreSQL 16 is het public-
-- schema niet schrijfbaar voor non-owners → eigenaarschap aan kc_user overdragen,
-- zodat Keycloak's Liquibase zijn tabellen kan aanmaken.
\connect keycloak
ALTER SCHEMA public OWNER TO kc_user;
GRANT ALL ON SCHEMA public TO kc_user;
\connect complidata
