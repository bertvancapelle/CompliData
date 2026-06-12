# SESSIESTART — CompliData V007

**Datum**: 2026-06-12
**Platform**: CompliData — een product van G. van Capelle Beheer B.V.

---

## Instructie voor CC bij sessiestart

1. Lees dit document volledig
2. Voer de sessiestart uit conform CLAUDE.md:
   - Controleer of .claude/skills/complidata/ bestaat
   - Zo ja: normale modus — lees alle complidata-skills + engineering/security
   - Zo nee: bootstrap-modus — lees alleen engineering/security
3. Lees SESSIE_BRIEFING.md voor de actuele projectstatus
4. Bevestig: "Sessiestart compleet — CompliData V007 — [N] skills geladen"
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

# SESSIE_BRIEFING.md — CompliData V007

**Gegenereerd**: 2026-06-12

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V007 |
| Datum | June 2026 |
| Commit | fb130df |
| Tests | 631 backend + 239 frontend groen |
| TST-rapport | TST-V007-Validatierapport.md |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
fb130df docs(kennisborging): patronen CD039–CD056 vastgelegd in skills/CLAUDE.md + ADR-022-voorbereiding + OPVOLGPUNTEN-sweep incl. OP-22-sluiting (CD057)
97a48cb feat(component): ADR-021 fase E — impactanalyse: read-only afhankelijkheids-traversal met readiness- en contractcontext (CD056)
8f44aff feat(component): ADR-021 fase D-2 v2 — verenigde Componenten-UI: convergente aanmaak, besturingskolommen, menu-sanering (CD054b)
a733039 fix(infra): Keycloak eigen database + named volume voor Postgres — lost COMPONENT-collision op en sluit OP-22 (CD055)
f8a70d9 refactor(component): ADR-021 fase D-1 — padconsolidatie app→component-contracten + ContractSectie-generalisatie (CD054a)
```

---

## Prioriteiten volgende sessie

# NEXT_SESSION.md — CompliData V007

**Gegenereerd**: 2026-06-12
**Vorige build (deze afsluiting)**: V006 → **V007**
**Laatste commit vóór de bump**: fb130df (CD057)

---

## Stand van zaken (V007)

Sessie CD039–CD058 bovenop V006 — twee ADR-blokken + infra + borging:

- **ADR-020 contractregister** (CD039–046): leverancier-/contractregister (RLS, CHECK/UNIQUE,
  platform-catalogus), tenant-UI, categorie-8-contextpaneel, catalogus-beheer-UI.
- **RLS-poolfix** (CD047/048): tenant-context transactie-lokaal (`after_begin`-hook) — 500-na-
  commit gedicht. **ZoekSelect** (CD049).
- **ADR-021 component-herfundering** (CD050–054, 056): supertype/subtype shared-PK, landschaps-
  graaf, verenigde Componenten-UI (convergente aanmaak + menu-sanering), impactanalyse.
- **CD055 Keycloak-scheiding** (eigen DB + named volume → OP-22 gesloten). **CD057 kennisborging**.
- **631 backend + 239 frontend** groen; 1 migratie (`0006_component_herfundering`).

---

## Top-5 prioriteiten volgende sessie (Bert prioriteert)

1. **ADR-022-afpelling** — checklist/beoordelingsprofiel per componenttype; werk de **vier open
   ontwerpvragen** uit `docs/adr/ADR-022_VOORBEREIDING.md` af (lifecycle vs. alleen scores;
   readiness-rapportage; configuratievorm; relatie tot het subtype-mechanisme).
2. **ADR-006 — audit-trail** (hash-chained, append-only). Het drie-lagen-advies ligt vast in de
   chat-besluiten; ADR-022 gaat **vóór** ADR-006 (audit logt het definitieve besturingsmodel).
3. **#16 — Tenant-/usermanagement-backend** (deblokkeert #15; platform-domein ADR-012, raakt
   OP-13 platform-tabel-grants).
4. **#14** (na ADR-006) en **#15** (na #16) — geblokkeerde backlog oppakken zodra hun
   afhankelijkheid staat.
5. **OP-28 VPS-deployment** t.z.t. (raakt OP-14 secrets-hardening) — alleen op Berts sein.

---

## Uitgestelde punten (achtergrond)

Zie `docs/OPVOLGPUNTEN.md`: OP-3 (refresh-token), OP-13 (platform-tabel-grants), OP-14 (secrets),
OP-20 (live NULLS-LAST), OP-21 (eigenaar distinct-dropdown), **OP-23** (cyclus-padbewaking bij
invoer), **OP-24** (C-drempel zoekvelden), **OP-25** (Uvicorn-accesslog timestamps), **OP-26**
(`component.eigenaar_organisatie` nullable), **OP-27** (dev-seed init-stap), **OP-28** (VPS).

---

## Werkwijze (triggerdiscipline)

Elke opdracht-`.md` begint op **regel 1** met `START: [taaknaam]`. **`AKKOORD: commit`** is
exclusief de commit-trigger op een groen eindrapport; "akkoord"/"doorgaan" stemt alleen met een
advies in. CC verifieert zélf de groene staat vóór elke commit. Reset-procedure (named volume +
handmatige dev-seed): `docs/LOKAAL-TESTEN.md`.


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — CompliData V007"
4. Wacht op START: [naam] van Bert

