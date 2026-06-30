# SESSIE_BRIEFING.md — LIKARA V026

**Gegenereerd**: 2026-06-30

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V026 |
| Datum | June 2026 |
| Commit | f7ecd7c |
| Tests | backend 931/2/0, frontend 745/745 |
| TST-rapport | TST-V026-Validatierapport.md |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
f7ecd7c refactor(schema): LI050 — audit-triggerfunctie cd_audit_append_only → lk_audit_append_only (S7)
d67e968 refactor(infra): cd_/complidata -> lk/likara — rabbit-user, vhost-prefix, MinIO-user, paden (S6, LI048)
28e421c fix(migratie): revisie-id 0043 <=32 tekens — verse provisioning brak op alembic_version varchar(32) (LI049)
4e0f6a0 refactor(misc): LI047 — S5 localStorage-key + backup-basisnaam cd/complidata → lk/likara
e9e4835 refactor(config): LI046 — S4 env-flags COMPLIDATA_* → LIKARA_* (test-mode/fixture-set)
```

---

## Prioriteiten volgende sessie

# LIKARA — Next Session (LI052)

> **Sessie LI051 (V026):** volledige code-rebrand `cd_`/`complidata` → `lk`/`likara`
> afgerond (LI038–LI050). De onderstaande top-5 is in V025 vastgesteld en deze sessie
> NIET opgepakt — blijft de prioriteit. Resterende rebrand-punten staan onderaan.

## Top-5 prioriteiten

1. **ADR-035 Slice 3** — Registratie onvolledig (score onder configureerbare drempelwaarde).
   Vereist platform-instelling (tenant-breed, default 80%). Aparte mini-slice.

2. **Modus ego→impact ontkoppelen van set-grootte** — automatische modus-wissel bij
   2+ set-leden voelt abrupt. Modus wordt expliciete gebruikerskeuze (tabs);
   ADR-033-revisie nodig.

3. **GebruikersgroepDetail — standalone pagina** — ontbreekt; gebruikersgroepen
   leven nu als sectie in ComponentDetail. Badge + signalering wachten hierop.

4. **BlokkadeDetail — standalone pagina** — ontbreekt; blokkades hebben alleen
   BlokkadeOverzichtView (lijst). Badge + signalering wachten hierop.

5. **Zoekbalk contextlabel** — "Component toevoegen aan beeld" boven de zoekbalk
   in kaart-modus (klein, cosmetic, 1 regel tekst).

## Openstaande punten (volledig)

### ADR-035 Signalering
- Slice 3: "Registratie onvolledig" (configureerbare score-drempelwaarde) — uitgesteld
- blokkade_zonder_eigenaar — structureel onmogelijk (roltoewijzing verwijst niet naar
  blokkade, blokkade is geen element-subtype); vereist schema-/semantiekherziening
- badges op GebruikersgroepDetail/BlokkadeDetail — uitgesteld tot detail-pagina's bestaan

### ADR-030
- Signaaltype "component zonder per-band dekking" als toekomstig ADR-035-signaaltype — genoteerd

### Landschapskaart
- Modus ego→impact ontkoppelen van set-grootte (ADR-033-revisie)
- Scope-balk gedrag in subgraaf-modus (bewust uitgesteld)
- Swimlane implementatie (ADR-034, geparkeerd)
- Saved views als permanente hoofdingang (Fase D)

### Platform
- GebruikersgroepDetail standalone pagina
- BlokkadeDetail standalone pagina
- fcose TOEGESTANE_ELEMENTEN uitbreiding (ADR-026-amendement, optioneel)

### Cosmetic/klein
- Zoekbalk contextlabel "Component toevoegen aan beeld" in kaart-modus

### Strategisch (parked)
- Export/import/rapportage — scope en fasering apart te bepalen

### Resterend uit de rebrand (LI038–LI050, geen code meer)
- **DC013** — GitHub-repo/remote `bertvancapelle/CompliData` → LIKARA + remote-URL;
  lokale map `~/complidata/` opruimen (stack draait op `~/likara/`). Berts GitHub-actie.
- **Deploy-side** — andere omgevingen: `.env`/secrets bijwerken (`RABBITMQ_URL`→`lk_rabbit`,
  `MINIO_ROOT_USER`→`likara_admin`, cookie-/env-namen) + re-provision.
- **env-test-robuustheid** (OP-30) — `test_callback_succes_zet_lk_session_cookie` laat
  `cookie_secure` van de omgeving afhangen; expliciet zetten.
- **Procesgat secrets-backup** — `~/likara/secrets/` gedocumenteerd maar feitelijk nooit gevuld → verzoenen.


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — LIKARA V026"
4. Wacht op START: [naam] van Bert
