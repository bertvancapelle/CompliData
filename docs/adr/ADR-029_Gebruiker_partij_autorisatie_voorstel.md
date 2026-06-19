# ADR-029 — Gebruiker-partij-koppeling + per-type gereedmeld-autorisatie

**Status:** Voorstel (geparkeerd — fundament voor eerste implementatie)
**Datum:** 2026-06-19
**Relatie:** Bouwt op ADR-010/012 (Keycloak-rollen, tweelaags rollenmodel), ADR-024 (partijenregister
+ persoon-partij) en ADR-027 (component-klaarverklaring — het grove gereedmeld-recht). Verfijnt het
ADR-027-recht; ADR-027 hangt NIET op ADR-029.
**Invariant (ongewijzigd):** score blijft de enige lifecycle-driver — de engine wordt niet geraakt.

---

## Context / aanleiding

Vandaag kent KILARA inloggers alleen als **Keycloak-token met een grove rol**
(viewer/medewerker/beheerder/auditor). Er is **geen blijvende "gebruiker" in de app** en **geen brug**
tussen de login en de **persoon in het partijenregister** (ADR-024): die twee werelden staan los
(bevestigd in het RBAC-feitenrapport DC014). De rechtenmatrix is een vaste platform-brede tabel
zonder per-tenant of per-persoon granulariteit; rol-toekenning loopt volledig via Keycloak; er is
geen tenant-gebruikersbeheer in de app.

Daardoor kan het systeem niet uitdrukken: *"déze persoon mag dít gereedmelden."* ADR-027 levert nu
het **grove** recht (de rol `KLAARVERKLARING` bepaalt wie mag aftekenen, ja/nee) plus volledige
**herleidbaarheid** (`verklaard_door`/`verklaard_op` + audit). Voor een eerste echte implementatie
is een fijner fundament nodig: **gebruikersbeheer van de eigen organisatie** + **gerichte
gereedmeld-autorisatie per componenttype**.

---

## Besluit (kern)

1. **Brug login ↔ persoon.** Een Keycloak-identiteit wordt gekoppeld aan een **persoon-partij** in
   de eigen organisatie (ADR-024). Selectief en optioneel: niet elke login is een persoon, en niet
   elke persoon logt in. De koppeling maakt "wie ben ik als ingelogde gebruiker, en welke persoon
   ben ik in het register" expliciet.
2. **Per-type gereedmeld-recht aan de persoon.** Een persoon krijgt het recht een component
   **gereed te melden** per **componenttype** (de platform-vaste, korte typelijst — geen explosie).
   Voorbeeld: "Piet mag type *Applicatie* gereedmelden." Het systeem **oordeelt niet over expertise**;
   de beheerder kent het recht toe op basis van zijn eigen oordeel.
3. **Beheerd door de beheerder, via een eigen recht.** Het uitdelen van gereedmeld-bevoegdheden is
   gevoeliger dan gewoon partijbeheer — je deelt **bevoegdheden** uit, geen gegevens. Daarom een
   **apart autorisatiebeheer-recht**, exclusief voor de beheerder, **gescheiden van het gewone
   `PARTIJ`-recht** (gegevensbeheer ≠ bevoegdheidsbeheer).
4. **Verantwoordingsketen.** *Wie-gaf-het-recht* én *wie-meldde-gereed* blijven **gescheiden
   herleidbaar** in de audit-trail: "beheerder X gaf Piet recht op type Applicatie op datum" naast
   "Piet meldde component Y gereed met reden op datum".

### Relatie tot ADR-027
ADR-027 = het **grove** recht (rol `KLAARVERKLARING`: mag aftekenen ja/nee) + volledige
herleidbaarheid via `verklaard_door`. ADR-029 **verfijnt** dat later naar **per-type per-persoon** —
**preventief** (geen gereedmeld-knop voor een type dat niet van jou is), bovenop de bestaande
herleidbaarheid. ADR-027 blijft zelfstandig werken zonder ADR-029.

---

## Model in detail

- **Login ↔ persoon:** een koppeling tussen de Keycloak-identiteit (`sub`/e-mail) en een
  `persoon`-partij (ADR-024) binnen de tenant. Eén persoon ↔ ten hoogste één login; een login zonder
  persoon-koppeling blijft mogelijk (grove rol blijft gelden).
- **Per-type gereedmeld-recht:** een **tenant-scoped toewijzing** *persoon × componenttype* — een
  registratie-feit, in lijn met `roltoewijzing` (ADR-024): eigen tabel, composiet-FK's naar het
  element/de persoon, FORCE RLS, audit op de allowlist. Componenttype is de platform-vaste sleutel
  (geen vrije tekst, geen tenant-eigen typeset).
- **Beheerrecht:** een nieuwe permissie-entiteit voor **autorisatiebeheer** (alleen beheerder),
  los van `PARTIJ`. Het uitdelen/intrekken van per-type-rechten loopt via die entiteit.
- **Handhaving bij gereedmelden:** de gereedmeld-actie (ADR-027 `maak_aan`/`wijzig_status`) checkt
  naast de grove rol óók het per-type-recht van de gekoppelde persoon voor het componenttype van het
  component. Backend handhaaft; frontend verbergt de knop preventief (affordance).

---

## Invarianten

- **Engine onaangeroerd** — autorisatie en koppeling voeden de score-engine niet.
- **Backend blijft enige handhaver** — de frontend is affordance (knop tonen/verbergen); een
  frontend-gatingbug mag nooit tot een autorisatie-omzeiling leiden.
- **Structureel boven conventioneel** — schema dwingt de toewijzings-/koppeling-invarianten af
  (FK/UNIQUE/RLS), niet alleen app-side.
- **NCSC-kader** (Nederlandse overheid), niet NIST.
- **Strikte scheiding gegevensbeheer ↔ bevoegdheidsbeheer** — partijgegevens beheren (`PARTIJ`) is
  iets anders dan bevoegdheden uitdelen (nieuw beheerrecht).

---

## Gevolgen

- Nieuw fundament: een **gebruiker-begrip in de app** (via de login↔persoon-koppeling) waar nu alleen
  een token bestaat — ontworpen zodat het kan groeien naar breder gebruikersbeheer.
- Nieuwe tenant-scoped tabel(len) (koppeling + per-type-toewijzing) + een nieuwe RBAC-entiteit voor
  autorisatiebeheer; RBAC-matrix-teltest beweegt mee.
- Audit: koppeling + toewijzing op de tenant-allowlist → uitdelen/intrekken append-only herleidbaar.
- ADR-027 slice 2/3 (UI/rapportage) kan vóór ADR-029 landen; de gereedmeld-knop gate't dan nog op de
  grove rol en wordt later verfijnd.

---

## Open subknopen (met voorlopige default)

1. **Koppeling login ↔ persoon: handmatig vs. e-mail-match.** *Default: handmatig aanwijzen door de
   beheerder (expliciet, controleerbaar); automatische e-mail-match uit Keycloak als latere hulp.*
2. **Waar leeft het per-type-recht:** nieuwe tenant-scoped tabel *persoon × componenttype* vs.
   uitbreiding op de persoon-partij. *Default: aparte toewijzingstabel (registratie-feit, net als
   `roltoewijzing`).*
3. **Verhouding tot de bestaande `KLAARVERKLARING`-rol:** vervangt of verfijnt. *Default: verfijnt —
   de grove rol blijft de poort "mag aftekenen", het per-type-recht beperkt binnen wie die rol heeft.*
4. **Reikwijdte gebruikersbeheer:** alleen gereedmeld-autorisatie, of breder fundament (algemeen
   gebruikersbeheer eigen organisatie). *Default: start bij gereedmeld; ontworpen zodat het kan
   groeien.*

---

## Bouw-fasering (indicatief, ná besluit)

1. **Feitenrapport auth/identiteit** — exacte stand login/token/persoon (read-only).
2. **Brug login ↔ persoon** — koppeling + beheer (handmatig aanwijzen). Gate.
3. **Per-type toewijzing + beheerscherm** — tabel persoon × componenttype + nieuw beheerder-recht. Gate.
4. **Handhaving bij gereedmelden** — de ADR-027-actie checkt het per-type-recht. Gate.
5. **Frontend** — gereedmeld-knop preventief verbergen per type (affordance). Doorloop.

Elke slice met engine-onaangeroerd-borging en de gangbare gate-discipline.
