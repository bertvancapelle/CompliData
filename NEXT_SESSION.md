# NEXT_SESSION.md — CompliData V008

**Gegenereerd**: 2026-06-13
**Vorige build (deze afsluiting)**: V007 → **V008**
**Laatste commit vóór de bump**: 5ac30d6 (ADR-022 Fase F)

---

## Stand van zaken (V008)

Sessie bovenop V007: **ADR-022 — beoordelingsprofiel/checklist per componenttype** volledig
afgerond (Fase A–F + Wijziging W1), plus een dev-infraverbetering.

- **ADR-022 A–C**: generiek `component_profiel` (shared-PK, migratie `0007`); engine per-type
  `aantal_vragen`-scoping (B); toestand-gebaseerde type-lock `SUBTYPE_HEEFT_DATA` + `type_wijzigbaar`
  + "wat verdwijnt" (C).
- **ADR-022 W1** (migratie `0008`): vragenset **tenant-eigendom** (RLS, composiet-FK), tenant-CRUD via
  `cd_app`, in-tenant fan-out, optie-/vraagbeheer verhuisd platform → tenant-facing, soft-deactivatie.
- **ADR-022 E–F** (migratie `0009`): tweede checklist-dragend type end-to-end (`checklist_dragend`-vlag,
  generieke profiel-creatie, type-generieke "start beoordeling", type-gescopete scoring); readiness-
  dashboard **per type** (Besluit 3).
- **Dev hot-reload**: `cd-api` lokaal met `uvicorn --reload` (prod-default ongemoeid).
- **567** backend-module + **72** platform (1 pre-existing env-auth-test) + **255** frontend groen.
  Migratie head `0009`.

---

## Top-5 prioriteiten volgende sessie (Bert prioriteert)

1. **ADR-006 — hash-chained audit-trail (#17)**. Volgende grote prioriteit. ADR-022 ging er bewust
   vóór, zodat de audit-trail het **definitieve** besturingsmodel logt (checklist/beoordeling per
   componenttype, tenant-eigen vragensets, type-lock, lifecycle). Append-only, nooit verwijderen.
2. **#16 — Tenant-onboarding + baseline-kopie vragenset**. De W1-knip: bij `POST /tenants` de baseline
   (89 applicatie-vragen + antwoordconfig) in de nieuwe tenant kopiëren (als `cd_app` met de nieuwe
   tenant-RLS-context). Vandaag seedt alléén `dev_seed` per tenant.
3. **#14** (na ADR-006) en **#15** (na #16) — geblokkeerde backlog oppakken zodra hun afhankelijkheid staat.
4. **OP-29** (impact-lens veldlabel `aantal_applicaties` → naamsmell) + **OP-30** (auth-cookie env-test)
   — kleine losse follow-ups.
5. **OP-28 VPS-deployment** t.z.t. (raakt OP-14 secrets-hardening) — alleen op Berts sein.

---

## Uitgestelde punten (achtergrond)

Zie `docs/OPVOLGPUNTEN.md` (incl. de V008-stand bovenaan): OP-3 (refresh-token), OP-13 (platform-tabel-
grants), OP-14 (secrets), OP-21 (eigenaar distinct-dropdown), OP-23 (cyclus-padbewaking bij invoer),
OP-24 (C-drempel zoekvelden), OP-25 (Uvicorn-accesslog timestamps), OP-26 (`component.eigenaar_organisatie`
nullable), OP-27 (dev-seed init-stap), OP-28 (VPS), **OP-29** (impact-lens label), **OP-30** (auth-cookie env-test).

---

## Werkwijze (triggerdiscipline)

Elke opdracht-`.md` begint op **regel 1** met `START: [taaknaam]`. **`AKKOORD: commit`** is exclusief
de commit-trigger op een groen eindrapport; "akkoord"/"doorgaan" stemt alleen met een advies in. CC
verifieert zélf de groene staat vóór elke commit. Dev: `cd-api` draait met `--reload` — code-/module-
wijzigingen worden automatisch opgepikt (geen recreate meer nodig). Reset-procedure (named volume +
handmatige dev-seed): `docs/LOKAAL-TESTEN.md`.
