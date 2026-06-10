# SESSIESTART — CompliData V006

**Datum**: 2026-06-10
**Platform**: CompliData — een product van G. van Capelle Beheer B.V.

---

## Instructie voor CC bij sessiestart

1. Lees dit document volledig
2. Voer de sessiestart uit conform CLAUDE.md:
   - Controleer of .claude/skills/complidata/ bestaat
   - Zo ja: normale modus — lees alle complidata-skills + engineering/security
   - Zo nee: bootstrap-modus — lees alleen engineering/security
3. Lees SESSIE_BRIEFING.md voor de actuele projectstatus
4. Bevestig: "Sessiestart compleet — CompliData V006 — [N] skills geladen"
5. Wacht op START: [naam] van Bert

---

## Interactieregel (VERPLICHT — niet-onderhandelbaar)

Geldt voor zowel CC als claude.ai, in elke sessie:

- Stel vragen ALTIJD één voor één. Stel nooit meerdere vragen tegelijk.
  Wacht op het antwoord van Bert voordat je een volgende vraag stelt.
- Geef adviezen ALTIJD één voor één. Geef nooit meerdere adviezen tegelijk.
  Wacht op de reactie van Bert voordat je een volgend advies geeft.

Deze regel is niet-onderhandelbaar en overschrijft elke neiging om
meerdere vragen of adviezen te bundelen.

---

## Opdrachtformaat CC-opdrachten (VERPLICHT — standaardwerkwijze)

claude.ai levert elke CC-opdracht ALTIJD aan als een .md-bestand
(downloadbaar), nooit als een los codeblok in de chat. Bert gebruikt dat
.md-bestand in CC. Deze afspraak geldt in elke sessie.

---

# SESSIE_BRIEFING.md — CompliData V006

**Gegenereerd**: 2026-06-10

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V006 |
| Datum | June 2026 |
| Commit | 0b0976b |
| Tests | 519 backend + 151 frontend groen |
| TST-rapport | TST-V006-Validatierapport.md |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
0b0976b docs(auth): OP-4 afgerond — RP-initiated logout reeds geïmplementeerd (CD038)
2a0b247 docs(auth): OP-7 afgerond — 401 reeds canoniek; stale docstrings + lock-test (CD037)
216eec7 docs(opvolgpunten): OP-16 afgerond — tenantSlug-getter reeds gefixt (CD036)
f5e1ccf feat(checklist): O2 — 7.5 BIO2-classificatie naar BBN1/2/3 via soft-deactivate (CD035)
67b0171 feat(frontend): ADR-019 fase 2E-c — beheer-UI ChecklistConfigBeheer (CD034)
```

---

## Prioriteiten volgende sessie

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


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — CompliData V006"
4. Wacht op START: [naam] van Bert

