# NEXT_SESSION.md — CompliData V005

**Gegenereerd**: 2026-06-08
**Vorige build (deze afsluiting)**: V004 → **V005** (gen_build bumpt de teller in fase 3)
**Laatste commit vóór de bump**: 23a3db8

---

## Stand van zaken (V005)

Sessie CD013–CD024 bovenop V004:

- **Dashboard tenant-breed** (lifecycle-telling, open blokkades, recent gewijzigd). [CD014, #9]
- **Server-side sorteerbare keyset-lijsten** (ADR-017, v2/v2n) + **applicatieregister-filter**
  (status/hostingmodel/eigenaar/zoek, LIKE-escaping). [CD015/CD017, #10]
- **Tenant-breed blokkadesoverzicht** (NULLS-LAST-keyset). [CD016, #12]
- **Sorteer-retrofit** van de 5 legacy-lijsten (datatype/gebruikersgroep/koppeling/
  checklistscore/blokkade-sectie) + **legacy-cursor opgeruimd**. [CD020/CD021]
- **Applicatie-detail → categorie-tabs** (2-laags, `AppTabs`, deep-link). [CD022, #11]
- **Koppelingenkaart** (gefocuste ego-graaf + toegankelijke relatietabel, ADR-018). [CD023, #13]
- **gen_build volgordefix** (bouwstatus vóór briefing-generatie). [CD018]
- **Patronen + commit-discipline vastgelegd** in de complidata-skills + CLAUDE.md/CONTRIBUTING §7. [CD024]
- **461 backend + 123 frontend-tests groen**; geen migraties deze sessie.

Backlog #1–#13 afgerond, **op #14 en #15 na** (geblokkeerd): #14 wacht op #17, #15 wacht op #16.

---

## Top-5 prioriteiten volgende sessie (Bert prioriteert)

1. **#16 — Tenant-onboarding / user-management-backend** (deblokkeert #15; platform-domein
   ADR-012/`cd_platform`, raakt OP-13 platform-tabel-grants).
2. **#17 — Audit-trail (ADR-006)** — hash-chained, append-only auditlog (deblokkeert #14).
3. **#15 (na #16)** en **#14 (na #17)** — de geblokkeerde backlog-items oppakken zodra hun
   afhankelijkheid staat.
4. **Productie-hardening**: OP-14 (dev-credentials vervangen), OP-7 (401/403 in hetzelfde foutformaat).
5. **Live-DB-verificatie (#23 / OP-20)**: NULLS-LAST-paginering empirisch tegen Postgres
   bevestigen (asc/desc over de NULL-grens).

---

## Uitgestelde punten

Zie `docs/OPVOLGPUNTEN.md`: OP-20 (NULL live-verificatie), OP-16-testrand (happy-dom
teardown-residu), OP-21 (eigenaar distinct-dropdown, optioneel). Productie-hardening: OP-7, OP-13, OP-14.
