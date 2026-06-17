# CompliData Changelog V011

**Datum**: 2026-06-17
**Sessie**: DC010
**Migratieketen**: t/m `0024_adr023_vraagbetekenis`
**Tests**: 746 backend + 311 frontend groen (1 pre-existing, omgevingsgebonden env-test `test_auth_pkce`)
**Kritieke bevindingen**: 0
**Invariant geborgd**: score blijft de enige lifecycle-driver — engine onaangeroerd in alle slices.

## Geland deze sessie (ADR-023 Fase F afgerond)

| Commit | Onderwerp |
|---|---|
| `d6ecc42` | **F-6** — `checklist_dragend`-drift hersteld (seed zet de vlag expliciet; demo-type → `client_software`) |
| `ec4f1ba` | **F-1** — migratielaag frontend-overzicht (Migratie-navgroep + plateau/gap/work-package/deliverable-lijsten) |
| `1b5fbb3` | Blokkade-herkomst op het component-scherm (kolom + doorklik) |
| `0d7a5cf` | Checklist/blokkade-weergaveverbeteringen (3 onderdelen) |
| `1faff1c` | Dashboard-statustegels klikbaar (status + type doorklik) |
| `80cfd54` | Status-filter → multi-select dropdown |
| `b81d8e8` | Componententabel server-side sorteerbaar (7 kolommen) |
| `4a1ae36` | **F-4** — platform-beheerscherm relatie-kenmerk-catalogus (`dispositie`/`relatie_rol` beheerbaar) |
| `77b643b` | **F-2** — cross-element laagprojectie (read-only architectuuroverzicht, beide typing-bronnen) |
| `69ae820` | **F-3 stap 1** — betekenis-marker op checklistvraag (catalogus + kolom + cross-tenant datamigratie) |
| `f5bc0ed` | **F-3 stap 2** — consistentie-signalering technische plaatsing (`GET /signalen/plaatsing` + view) |

## Migraties

`0023_checklist_dragend_fix` · `0024_adr023_vraagbetekenis` — additief; ID's ≤32 tekens.
`0024` voegt de platform-brede `vraagbetekenis_optie`-catalogus (geen RLS) + `checklistvraag.betekenis`
(nullable, `UNIQUE(tenant_id, componenttype, betekenis)` met NULL-distinct → geen partial index) toe, plus
een **cross-tenant datamigratie** (als cd_admin/superuser, bypasst FORCE RLS) die `technische_plaatsing`
op de applicatie-plaatsingsvraag (`2.2`) over álle tenants zet.

## Nieuwe API / semantiek

- **F-3 betekenis-marker**: tenant-beheer `GET /checklistconfig/betekenissen` + `PATCH /vragen/{id}/betekenis`
  (`CHECKLISTVRAAG.WIJZIGEN`); classificatie, geen fan-out.
- **F-3 signalering**: `GET /signalen/plaatsing` (`ARCHITECTUUR.LEZEN` hergebruikt) — read-only afgeleid uit
  betekenis-markering × `draait_op` (assignment `doel==component`); generiek over componenttypen; twee zachte
  signalen (beoordeeld-niet-vastgelegd / vastgelegd-niet-beoordeeld). Bewust geen paginering (begrensd rapport).
- **F-2 architectuur**: `GET /architectuur/elementen` (cross-element laagprojectie).
- **F-4**: platform `/platform/relatiekenmerkconfig` (beheer relatie-kenmerk-catalogus).

## Skills bijgewerkt

`complidata-db` (cross-tenant datamigratie via cd_admin-superuser; classificatie-marker-patroon; NULL-distinct
uniciteit; expand/contract bij marker), `complidata-backend` (signalering = read-only afleiding op markering;
engine-borging-verfijning bij read-of-score; seed-locatie; validator-signaturen), `complidata-tests`
(live signaal-fixtures; OPVOLGPUNTEN-tracked + gerichte staging; dev-ergonomie psql/find-delete),
`complidata-frontend` (read-only lees-views + nav-gating; test-router-gotcha; leesbare signaaltekst).

## Aandachtspunt

- **OPVOLGPUNTEN.md is feitelijk tracked** (niet untracked zoals bouwopdrachten aannemen) — te beslissen in
  de volgende sessie (officieel tracked behandelen óf gitignoren).
