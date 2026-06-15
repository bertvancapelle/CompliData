# OPVOLGPUNTEN — CompliData

Geparkeerde punten en volgende prioriteiten. Bijgewerkt bij sessie-afsluiting.
**Stand**: build **V010** (sessie DC009), migratie head **`0021`**, commit-basis `2dc38aa`
(ADR-023 Fase E E3 — Deliverable).

---

## Volgende prioriteiten

1. **ADR-023 Fase E — E4 (Gap + readiness-rollup).** De afsluitende Fase-E-slice. Gap = geregistreerd
   object met **vaste 2-ariteit** baseline- + doel-plateau (FK-kolommen op het gap-subtype, géén
   relatie — uitzondering op de facade-over-Relatie-conventie). **Readiness = ROLLUP** puur read-only
   afgeleid uit de bestaande lifecycle van de gap-componenten (geen opgeslagen tweede bron): alleen
   checklist-dragende leden hebben een lifecycle; niet-dragende leden vallen buiten de noemer.
   Schema-rakend → **gate** vóór commit.
2. **ADR-023 Fase F.** Gelaagde ArchiMate-lees-API + gap/plateau-/migratie-views (frontend) +
   **E-8 checklist-consistentiecheck** (technische plaatsing: antwoord-ja ↔ bestaan draait_op-relatie —
   read-only **signalering**, geen engine-poort) + RBAC/audit-afronding. Open Exchange-export blijft
   buiten scope.

---

## Geparkeerde follow-ups (bewust uitgesteld)

1. **Platform-beheerscherm voor de relatie-kenmerk-catalogus ontbreekt.** `dispositie` + `relatie_rol`
   zijn geseed en werken in de gebruiker-dropdown (`/contracten/opties` componeert relatie_rol uit de
   nieuwe catalogus), maar er is nog géén platform-beheer-UI/endpoint voor `relatiekenmerk_optie` —
   `relatie_rol` is daardoor tijdelijk niet via een beheerscherm bewerkbaar. → **Fase F**.
2. **Latente inconsistentie `applicatie.checklist_dragend`-vlag.** De catalogus heeft `applicatie=false`
   terwijl migratie `0009` hem op `true` zet; de **seed zet de vlag niet** → na een DB-reset wint
   `seed=false`. Breekt nu niets (het applicatie-pad is **hardgecodeerd** en negeert de vlag — subtype +
   profiel onvoorwaardelijk), maar **de vlag liegt**. Op te lossen drift — bewust inplannen vóór code de
   vlag voor `applicatie` gaat vertrouwen (aannemelijk in Fase E/F). (`applicatieserver=true` in dev is
   een **dev-seed-demo-artefact**, geen platform-default; de platform-seed zet géén enkel type dragend.)
3. **"checklist-dragend maken" als echte beheerder-functie = productkeuze (geen bug).** Vandaag alleen
   via code/migratie/SQL instelbaar (`ComponentConfigOptieUpdate` kent de vlag niet). Een type dragend
   maken vereist ook **type-specifieke checklistvragen** (per componenttype, ADR-022 W1); zonder vragen
   blijft de lifecycle structureel op `in_inventarisatie`. → **Fase F / onboarding**.

---

## Lopende conventies (blijvend van kracht)

- **Migratie-ID ≤32 tekens** (`alembic_version` = `varchar(32)`) — harde conventie.
- **Live-test-teardown ruimt element-residu structureel op** (V009-follow-up a) — toegepast in alle
  E-slices (plateau/work_package/deliverable): residu-check ná de run = 0.
- **Gate-per-schema-slice** (nieuwe tabel/RLS/migratie/RBAC/audit) → bouwen + testen + gate-rapport,
  pas commit ná `AKKOORD: commit`. Doorloop-met-commit alléén voor licht/additief (read-side/frontend/
  docs). Vastgelegd in de complidata-skills (db/backend/tests, bijgewerkt V010).

---

## Eerder geparkeerd (achtergrond, nog open)

- **(d) Pre-existing env-test** `test_auth_pkce.py::test_callback_succes_zet_cd_session_cookie` — faalt
  omgevingsgebonden (Secure-cookievlag in test/dev), DB-onafhankelijk; in de huidige omgeving groen. Te
  onderzoeken: de Secure-cookie-assertie omgevings-onafhankelijk maken.
- Achtergrond-uitstelpunten (OP-3 refresh-token-realm-hardening/OP-14 secrets, VPS-deploy OP-28 e.a.):
  zie de changelog-historie; niet sessie-kritiek.
