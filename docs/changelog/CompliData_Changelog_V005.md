# CompliData Changelog V005

**Datum**: 2026-06-08

## Wijzigingen

Sessie CD013–CD024 bovenop V004:

- **Dashboard tenant-breed** — lifecycle-telling, open blokkades, recent gewijzigd. [CD014, #9]
- **Server-side sorteerbare keyset-paginering** (ADR-017, v2/v2n) op de Applicatie-lijst,
  + **applicatieregister-filter** (status/hostingmodel/eigenaar/zoek, LIKE-escaping). [CD015/CD017, #10]
- **Tenant-breed blokkadesoverzicht** met NULLS-LAST-keyset. [CD016, #12]
- **gen_build volgordefix** — bouwstatus-update vóór de briefing-generatie. [CD018, OP-18]
- **Sorteer-retrofit** van de 5 legacy-lijsten (datatype/gebruikersgroep/koppeling/
  checklistscore/blokkade-sectie); koppeling incl. tegenpartij-naam-join. [CD020]
- **Legacy-cursor opgeruimd** (`encode/decode_cursor`) na de retrofit. [CD021]
- **Applicatie-detail → categorie-tabs** (2-laags, `AppTabs`, deep-link, behoud functionaliteit). [CD022, #11]
- **Koppelingenkaart** — gefocuste ego-graaf (hand-rolled SVG) + toegankelijke relatietabel,
  ADR-018; geen nieuwe dependency. [CD023, #13]
- **Test-hygiëne** — happy-dom unhandled rejection in `useTheme`/`tenantId.test.js` opgelost. [CD019, OP-16-rand]
- **Patronen vastgelegd** in de complidata-skills (db/frontend/backend) + commit-discipline in
  CLAUDE.md/CONTRIBUTING §7. [CD024]

**ADR's**: ADR-017 (sorteerbare keyset, V004) en **ADR-018** (relatievisualisatie: gefocuste
ego-graaf, geen graaf-dependency, toegankelijk tabel-alternatief) toegevoegd.

**Tests**: 461 backend + 123 frontend groen · 4 assen + 2 poorten · 0 kritieken. Geen migraties.

**Open / vooruit**: #16 (tenant-onboarding/user-management) en #17 (audit-trail, ADR-006) als
opvolgers; OP-22 (backup-scope/Keycloak-secrets, dev-risico geaccepteerd, vóór productie oplossen).
