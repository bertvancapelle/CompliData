# TST-V007 — Validatierapport

| Veld | Waarde |
|------|--------|
| Build label | V007 |
| Datum | 2026-06-12 |
| Vorige build | V006 |
| Kritieke bevindingen | 0 |

Deze sessie (CD039–CD058) leverde twee grote ADR-blokken plus infra- en kennisborging:
het **ADR-020 contractregister** (leverancier-/contractregister met platform-catalogus,
tenant-UI en categorie-8-context), de **ADR-021 component-herfundering** (supertype/subtype
shared-PK, landschapsgraaf, verenigde Componenten-UI met convergente aanmaak, impactanalyse),
de **infra-fix CD055** (Keycloak eigen database + named volume — sluit OP-22), en de
**kennisborging CD057**. Twee structurele incidentfixes (RLS-poolcontext CD048;
COMPONENT-collision CD055). Validatie omvat de 4 backend-assen **plus** de frontend-poorten.

## Backend — 4 assen (CONTRIBUTING.md §6)

| As | Commando | Verwacht | Resultaat |
|----|----------|----------|-----------|
| 1 — py_compile | `find … \| xargs py_compile` | 0 syntaxfouten | **Geslaagd** — 0 projectfouten |
| 2 — pytest | `python3 -m pytest backend/tests/ modules/ -q` | alle groen | **Geslaagd** — **631 passed** |
| 3 — Alembic | `alembic heads` / `branches` | 1 head, 0 branches | **Geslaagd** — 1 head `0006_component_herfundering`, 0 branches |
| 4 — referentie-grep | grep `Eraneos\|compliman\|cm_` | 0 hits | **Geslaagd** — 0 hits (backend/frontend/modules/docs) |

## Frontend — poorten

| Poort | Verwacht | Resultaat |
|-------|----------|-----------|
| `vite build` | 0 fouten, geen chunk >500 kB | **Geslaagd** — grootste chunk `column` (PrimeVue DataTable, lazy) 379 kB, entry `index` ≈ 169 kB |
| `vitest run` | alle groen | **Geslaagd** — **239 passed** (35 bestanden) |

## Empirische live-verificaties deze sessie

| CD | Verificatie | Resultaat |
|----|-------------|-----------|
| CD040 | Contractregister: RLS-isolatie + grants + CHECK/UNIQUE-invarianten (14 checks) | Groen |
| CD044/045 | Browser-walkthroughs contractoverzichten + categorie-8-paneel | Groen |
| CD048 | Koude-pool-burst **6×201**, cross-tenant-wisseltest, context-isolatie | Groen |
| CD054b-v2 | Browser-walkthrough verenigde Componenten-UI (convergente aanmaak, menu-sanering) | Groen |
| CD055 | Keycloak-scheiding: realm-import op eigen DB, **reset-proof** (2× `down -v && up -d`), dump **Keycloak-vrij** (OP-22-sluiting) | Groen |
| CD056 | Impactanalyse: directe/transitieve afhankelijkheid + **cyclus-terminatie** (A↔B) | Groen |

## Incidenten + structurele fixes

- **500-na-commit (CD047-diagnose → CD048-fix)**: een geslaagde INSERT gevolgd door
  `commit`→`refresh` raakte een **contextloze poolverbinding** (`''::uuid`). Les: tenant-context
  moet **transactie-lokaal** zijn (`set_config(..., true)` via een `after_begin`-hook op
  RLS-sessies), niet eenmalig per sessie (`false`). Duplicaat-/cross-tenant-risico gedicht.
- **COMPONENT-collision + ineffectieve reseed (CD055)**: Keycloak deelde `complidata/public`;
  de ADR-021-tabel `component` schaduwde Keycloak's interne `COMPONENT` → Keycloak startte niet.
  Tevens: Postgres-data stond op een **host-bind-mount**, dus `down -v` reset niets. Les:
  Keycloak hoort een **eigen database** (`keycloak`/`kc_user`) en de DB-data op een **named
  volume**; de gedocumenteerde reseed klopt daarna weer.

## Baselines V007 (benoemd)

| Categorie | Telling |
|---|---|
| componenten | **14** (12 applicatie-subtypen + Oracle FIN-DB + Geo-fileshare) |
| structuurrelaties | **3** |
| leveranciers / contracten | **4 / 7** |
| app-koppelingen / contract-koppelingen | **10 / 11** |
| engine: applicaties / blokkades | **12 / 10** |
| catalogi: component / contract | **9 (7+2) / 9** |
| checklistvragen | **89** |

## ADR's deze sessie

- **ADR-020** — leverancier-/contractregister (Aanvaard, CD039 e.v.).
- **ADR-021** — component-herfundering (supertype/subtype shared-PK, landschapsgraaf), incl.
  Wijziging W1 (verenigde Componenten-UI, CD054b) en realisatienotitie shared-PK (CD051).
- **ADR-022 (voorbereiding)** — checklist per componenttype (Voorgenomen, CD057).

## Niet-blokkerende noten / geaccepteerde afwijkingen

- **OP-22 gesloten** (CD055): de `complidata`-dump bevat geen Keycloak-schema meer.
- **Dev-seed** is een bewuste **handmatige** fixture (niet in de init-container, dev-only);
  reset-procedure in `docs/LOKAAL-TESTEN.md`. Automatisering = OP-27 (nice-to-have).
- **422 = native FastAPI** `{detail:[…]}` — canoniek (ADR-014); 401/403/404/409 envelope.
- **Frontend-teardown-`DOMException`** (happy-dom thema-stylesheet-`fetch`) op stderr — bekende
  ruis, geen testfout. Nieuwe achtergrond-opvolgpunten: OP-23 t/m OP-27, OP-28 (VPS).
