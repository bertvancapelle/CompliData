# ADR-012 — Addendum A: `PlatformEntiteit.CHECKLISTCONFIG`

**Status**: Aanvaard (juni 2026)
**Hoort bij**: ADR-012 (tweelaags rollenmodel platform/tenant), ADR-019 (configureerbare
antwoordopties per checklistvraag).

## Context

ADR-019 introduceert een platform-brede configuratie van checklist-antwoordtypes en
-optiesets (referentiedata, beheerd op het platformniveau — ADR-019 Besluit 9). Om de
beheer-endpoints (ADR-019 fase 2D) schoon te kunnen autoriseren, is een nieuwe entiteit in de
platform-RBAC-matrix nodig; de bestaande entiteiten (`TENANT`, `PLATFORMINSTELLINGEN`,
`PLATFORMMETADATA`) dekken deze configuratie niet.

## Besluit

1. Nieuwe entiteit **`PlatformEntiteit.CHECKLISTCONFIG`** in `core/platform_rbac.py`.
2. Rechtenverdeling:
   - **platformbeheerder**: `L, A, W` (Lezen, Aanmaken, Wijzigen).
   - **platformoperator**: `L` (alleen Lezen).
3. **Geen `V` (Verwijderen)** voor wie dan ook: een optie wordt nooit hard verwijderd maar
   **soft-gedeactiveerd** (ADR-019 Besluit 9) — dat is een `W`-actie, geen `V`.

## Gevolgen

- Alleen de **platformbeheerder** kan antwoordtypes zetten en optiesets aanpassen
  (toevoegen / label & volgorde wijzigen / soft-deactiveren). De **platformoperator** mag de
  configuratie inzien maar niet wijzigen.
- Consistent met de tweelaags-logica: referentiedata-beheer leeft op het platformniveau
  (`cd_platform`), tenant-rollen raken het niet.
- Sluit aan op de grants uit ADR-019 fase 2A (`cd_platform` schrijft op `checklistvraag` en
  `checklistvraag_optie`; `cd_app` leest alleen).

## Niet in scope

- Per-tenant configuratie of -overrides (ADR-019: platform-breed).
- De beheer-UI in de SPA (ADR-019 fase 2E) — afhankelijk van platform-login in de frontend,
  apart te beslissen.

## Implementatie

Geïmplementeerd in **CD031** (fase 2D): `PlatformEntiteit.CHECKLISTCONFIG` + matrixrij
(beheerder `{L,A,W}`, operator `{L}`, geen `V`) in `core/platform_rbac.py`; de
`/platform/checklistconfig`-endpoints zijn geguard met
`vereist_platform_permissie(CHECKLISTCONFIG, …)` op `get_platform_session` (cd_platform).
RBAC-matrixtest uitgebreid (4 entiteiten × 2 rollen × 4 acties).
