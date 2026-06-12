# ADR-012 — Addendum C: `PlatformEntiteit.COMPONENTCONFIG`

**Status**: Aanvaard (CD006-sessie)
**Hoort bij**: ADR-012 (tweelaags rollenmodel platform/tenant), ADR-021 (component-herfundering),
ADR-012 Addenda A (`CHECKLISTCONFIG`) en B (`CONTRACTCONFIG`) — het patroon dat dit Addendum volgt.

## Context

ADR-021 introduceert twee platform-brede, beheerbare classificatie-catalogi (B2, besloten):
**componenttype** en **structuurrelatie_type**, samen in één tabel `componentconfig_optie` met
een `dimensie`-discriminator (zelfde vorm als `contractconfig_optie`). Voor de beheer-endpoints
is een nieuwe entiteit in de platform-RBAC-matrix nodig; de bestaande entiteiten dekken deze
catalogus niet.

## Besluit

1. Nieuwe entiteit **`PlatformEntiteit.COMPONENTCONFIG`** in `core/platform_rbac.py`.
2. Rechtenverdeling: **platformbeheerder `L, A, W`** · **platformoperator `L`**.
3. **Geen `V`** voor wie dan ook: soft-deactivate (`actief=false`) is een `W`-actie; opties
   worden nooit hard verwijderd.
4. **Eén entiteit voor beide dimensies** (componenttype / structuurrelatie_type) — de dimensie
   is een attribuut, geen autorisatiegrens.
5. **Systeem-sleutel-bescherming**: de optie `componenttype.applicatie` is gekoppeld aan het
   subtype-mechanisme (ADR-021 Besluit 8) en is **niet deactiveerbaar en niet muteerbaar** — de
   service weigert `actief=false`, sleutel- of dimensie-wijziging op deze rij (422-envelope).
   Label/volgorde wijzigen mag wél.

## Gevolgen

- Alleen de platformbeheerder beheert component- en structuurrelatie-typen; de operator leest.
- Consistent derde lid van de catalogus-familie (`CHECKLISTCONFIG`, `CONTRACTCONFIG`,
  `COMPONENTCONFIG`): identieke grants (`cd_app` SELECT-only, `cd_platform` CRUD zonder DELETE),
  identiek beheer-UI-patroon.

## Niet in scope

- Per-tenant configuratie of -overrides (platform-breed, conform ADR-020 B1-lijn).
- Autorisatie per dimensie.
- De tenant-data uit ADR-021 (`component`, `applicatie`, relaties) — RLS-scoped onder `cd_app`.

## Implementatie

Te realiseren in de ADR-021-fase die de platform-beheer-endpoints oplevert:
`PlatformEntiteit.COMPONENTCONFIG` + matrixrij in `core/platform_rbac.py`; de
`/platform/componentconfig`-endpoints geguard met `vereist_platform_permissie(COMPONENTCONFIG, …)`
op `get_platform_session`; de RBAC-matrixtest breidt uit naar 6 entiteiten; de
systeem-sleutel-bescherming (Besluit 5) krijgt eigen tests.
