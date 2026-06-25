# SESSIESTART — LIKARA V022

**Datum**: 2026-06-25
**Platform**: LIKARA — een product van G. van Capelle Beheer B.V.

---

## Instructie voor CC bij sessiestart

1. Lees dit document volledig
2. Voer de sessiestart uit conform CLAUDE.md:
   - Controleer of .claude/skills/complidata/ bestaat
   - Zo ja: normale modus — lees alle complidata-skills + engineering/security
   - Zo nee: bootstrap-modus — lees alleen engineering/security
3. Lees SESSIE_BRIEFING.md voor de actuele projectstatus
4. Bevestig: "Sessiestart compleet — LIKARA V022 — [N] skills geladen"
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

# SESSIE_BRIEFING.md — LIKARA V022

**Gegenereerd**: 2026-06-25

---

## Bouwstatus

## Actuele bouwstatus

| Veld | Waarde |
|------|--------|
| Build | V022 |
| Datum | June 2026 |
| Commit | fec08d5 |
| Tests | 896 backend + 654 frontend groen (2 skipped; 8 pre-existing seed-drift) |
| TST-rapport | TST-V022-Validatierapport.md |
| Kritieke bevindingen | 0 |

---

## Recente commits

```
fec08d5 feat(landschapskaart): set-scoped subgraaf + leverancier-filter + eigenaar-edge (vertrekpunt fase A) — LI021
ae905c1 seed(verrijking): infra-laag + samenstelling + scope-gaten in _seed_bvowb_scenario — LI021
0c4371b test(hygiene): live-DB-tests zelf-opruimend via finally — LI021
6129d48 docs(rename): complidata-merknaam → LIKARA in levende docs/comments (LI021 Fase 1)
98e957b chore(release): V021 afsluiting LI020 — skills + TST + changelog + bouwstatus + sessiestart
```

---

## Prioriteiten volgende sessie

# NEXT_SESSION.md — LIKARA V022

**Gegenereerd**: 2026-06-25 (sessie-afsluiting LI021)
**Build**: V021 → **V022**
**Migratie head**: `0042` (`0042_adr033_opgeslagen_view`) — geen schema-/migratiewijziging in LI021 (test-hygiëne = test-only; seed-verrijking = data-only; fase A = additieve read-only projecties/filter)
**Tests**: frontend **654 groen (62 files)** + `vite build` ok + `test:css-build` ok; backend **896 passed / 2 skipped / 8 pre-existing live-DB-failures** (seed-drift — zie TST-rapport). Zie `docs/TST-V022-Validatierapport.md`.

---

## Stand van zaken (V022) — test-hygiëne + seed-verrijking + kaart-vertrekpunt fase A

Deze sessie (LI021):

- **Test-hygiëne** (`0c4371b`) — twee live-DB-tests zelf-opruimend via `finally` (cleanup draait ook bij
  falen → geen residu-lek meer; vervuilings-cirkel gebroken).
- **Seed-verrijking** (`ae905c1`, data-only/idempotent in `_seed_bvowb_scenario`): infrastructuur
  (technology-laag) + draait-op-relaties; component-samenstelling (Burgerzaken-suite); bewuste scope-gaten
  (Archiefbeheer zonder eigenaar; Klantportaal uitsluitend organisatieloos gebruikt).
- **Kaart-vertrekpunt fase A** (`fec08d5`, additief/read-only): POST `/landschapskaart/subgraaf` (set-scoped
  S+1-hop; `component_ids=None` = volledige graaf, back-compat); leverancier-filter op `/componenten`
  (afgeleide EXISTS, beide paden); eigenaar-edge "is eigendom van" (context, **niet** in `IMPACT_RINGEN`).
  Dekt meteen het geparkeerde "scopebalk-tekent-organisaties"-spoor af.

---

## Top-5 prioriteiten volgende sessie (LI022) — in volgorde (leunt op elkaar)

1. **Reset + seed-herijking (EERST)** — de 8 pre-existing live-DB-failures groen krijgen in CC's omgeving:
   `docker compose down -v` → reseed (**handmatige dev-seed!** — `docker compose exec <api> python dev_seed_testdata.py`)
   + de stale tests herijken op `_seed_bvowb_scenario` (ze verwachten dode-seed-rijen — `GeoWorks
   Licentieovereenkomst`/`Oracle FIN-DB`/3 `client_software`-vragen — die de verrijkte seed niet maakt).
2. **Kaart-vertrekpunt fase B** — leeg openen + zoek-vertrekpunt via `/componenten`
   (naam/type/laag/hosting/eigenaar/leverancier) → set-opbouw → POST subgraaf, met accumulerende
   sub-graaf-cache. Besloten: selectie = alléén component-ids (org/leverancier = criterium + context);
   **cache weggooien** bij "begin opnieuw"; **1-hop norm, dieper alleen via doorklikken**; endpoint = POST.
3. **Fase C** — defaults omdraaien (leeg openen consistent: scopebalk niets-aan→alles + startscherm
   geen-views→hele model wég) + "zoek-erop-dan-toon-het" (auto-ring-activering op zoek, handmatig wint).
4. **Fase D** — opgeslagen views permanent náást het zoekveld (hoofdingang).
5. **Overige open punten** (ongewijzigd): ADR-034 open subknopen; interactieve legenda als type-filter;
   ADR-030 contract-dekking; ADR-029 Fase 5; klaarverklaring-blok op ComponentDetail; signalerings-ADR;
   dode-code-opschoning; cytoscape-dagre opruimen.

Volledige backlog: `docs/OPVOLGPUNTEN.md` (sectie "Stand V022 (LI021)").

---

## Bekende risico's en aandachtspunten

- **8 pre-existing live-DB-failures** — **seed-drift** (tests asserteren op rijen die `_seed_bvowb_scenario`
  niet maakt). De `finally`-hygiëne brak de residu-cirkel, maar de drift blijft → wordt door LI022-stap 1
  opgelost. NIET als opgelost markeren tot ze in CC's omgeving groen zijn.
- **Na elke `docker compose down -v` moet de dev-seed handmatig** (de init-container draait alleen
  `alembic upgrade head` + `platform_init`, niet de dev-seed). Vergeten = lege scenario-data.
- Worktree is **schoon**, niets ongecommit.

---

## Geleerde patronen deze sessie

Verwerkt in de complidata-skills (backend, frontend, ux, tests): kaart laadt nooit de volledige graaf bij
schaal (set + 1-hop via POST `/landschapskaart/subgraaf`; set-scoping = where-filter omdat de
ring-classificatie al `bron/doel ∈ id-set` was); vertrekpunt = zoeken, niet "alles tonen" (leeg openen,
selectie bevat componenten, org/leverancier = criteria); accumulerende sub-graaf-cache + incrementeel
bijladen; "zoek-erop-dan-toon-het" (handmatige ring-vink wint); eigenaar-edge als context (niet in impact);
leverancier = afgeleide EXISTS-filter; geen betuttelende scenario-regels (vrijheid + schone "begin opnieuw");
na `down -v` dev-seed handmatig; live-DB-tests self-contained + drift ≠ residu.


---

## Instructie voor CC

1. Lees deze briefing volledig
2. Lees CLAUDE.md (sessiestart-protocol)
3. Bevestig: "Sessie-briefing geladen — LIKARA V022"
4. Wacht op START: [naam] van Bert

