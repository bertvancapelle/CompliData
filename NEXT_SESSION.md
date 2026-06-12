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
