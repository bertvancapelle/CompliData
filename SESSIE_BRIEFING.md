# SESSIE_BRIEFING.md — CompliData V001

**Gegenereerd**: 2026-06-05

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V001 |
| Datum | Juni 2026 |
| Commit | — |
| Tests | 0 passed (nieuw platform) |
| TST-rapport | — |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
3bf70b5 docs: NEXT_SESSION.md invullen — top-5 prioriteiten sessie 2
e9913ea docs: generiek implementatieplan CompliData platform
fcf441a docs(tst): TST-V001 validatierapport
5c0707b feat(skills): vul 6 complidata-skills met V001-patronen
45ecf0c fix(infra): verwijder alle resterende CompliMan-referenties uit CompliData
```

---

## Prioriteiten volgende sessie

# NEXT_SESSION.md — CompliData V001

**Gegenereerd**: 2026-06-05
**Vorige build**: V001

---

## Top-5 prioriteiten sessie 2

1. **Architectuurcorrectie — ChecklistVraag platform-initialisatie**
   `seed_checklist_vragen()` verplaatsen van tenant-seed naar
   platform-initialisatie. Aanroepen bij `alembic upgrade head`
   voor het gehele platform. Zie IMPLEMENTATIEPLAN.md §Architectuurcorrectie.

2. **Keycloak PKCE login/callback — ADR-002**
   `/auth/login` en `/auth/callback` implementeren zodat de
   applicatie daadwerkelijk inlogbaar is. Inclusief token-uitwisseling
   en httpOnly cookie-sessie.

3. **RBAC rollenstructuur — ADR-010**
   `_load_roles()` invullen. Vier rollen implementeren:
   Viewer, Medewerker, Beheerder, Auditor. Keycloak-rollen
   koppelen aan platform-RBAC.

4. **Live DB-run verifiëren**
   `docker compose up` → `alembic upgrade head` →
   RLS-isolatietest (cross-tenant query moet 0 resultaten geven) →
   seed verificeren (89 checklistvragen aanwezig).

5. **Applicatie CRUD-laag — eerste module-endpoints**
   `GET/POST/PUT/DELETE /api/v1/applicaties` met
   lifecycle-handhaving in de service-laag.
   Eerste stap naar een werkende module-API.

---

## Openstaande beslissingen

- Branding-tokens: huisstijl G. van Capelle Beheer B.V. nog niet
  bepaald — base.css bevat placeholder-palet
- Domeinnaam voor productie-deployment: nog niet vastgesteld
- Tenant-onboarding flow: nog te ontwerpen (hoe wordt een nieuwe
  klant ingericht?)

---

## Bekende risico's en aandachtspunten

- Live DB-run nog niet gedraaid — RLS-isolatie en seed zijn
  alleen via SQL-preview geverifieerd, niet live
- RBAC-stub (_load_roles → []) betekent dat alle endpoints
  momenteel geen autorisatie uitvoeren
- Audit trail (ADR-006) nog niet gebouwd — mutaties worden
  nog niet gelogd

---

## Technische schuld

- SyntaxWarning in overgenomen framework-skill
  (ms365-tenant-manager/scripts/powershell_generator.py:242)
  — geaccepteerd als TST-V001-K1, buiten CompliData-scope
- PrimeVue branding-tokens zijn placeholder-palet —
  aanpassen zodra huisstijl bekend is

---

## Geleerde patronen sessie 1

Vastgelegd in .claude/skills/complidata/ (6 skills, V001):
- App-factory + lifespan patroon (backend)
- Alembic multi-location module-wiring (db)
- RLS + GRANT boilerplate per tabel (db)
- PostgreSQL enum-types in migraties (db)
- PrimeVue Unstyled + --cd- token-prefix (frontend)
- httpOnly cookie-auth patroon (security)
- conftest.py sys.path-setup voor module-tests (tests)
- Health degraded/ok patroon (resilience)
- Sessie-afsluit infrastructuur (gen_build, sluit_acties, TST)


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — CompliData V001"
4. Wacht op START: [naam] van Bert
