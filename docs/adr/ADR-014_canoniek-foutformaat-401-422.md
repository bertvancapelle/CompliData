# ADR-014 — Canoniek foutformaat: 401 gelijktrekken, 422 bewust native

| | |
|---|---|
| **Status** | Aanvaard |
| **Datum** | 2026-06-07 |
| **Beslissers** | Bert van Capelle (G. van Capelle Beheer B.V.) |
| **Gerelateerd** | OP-7 · ADR-003 (multi-tenant RLS) · ADR-010 (tenant-RBAC) · ADR-009 (BWB-module) |

## Context

De API kent een canoniek foutenvelope `{"fout":{"code","http_status","bericht"}}`,
gedefinieerd via domeinexcepties + handlers (`modules/.../services/errors.py`,
analoog aan `OnvoldoendeRechten`). Dat envelope dekt vandaag **403, 404 en 409**.

Twee statussen wijken af:

- **401** volgt nog het oude `{"detail":{"code":…}}`-patroon van de auth-laag.
- **422** is de standaard-FastAPI-validatiefout: een **lijst** veldfouten
  `{"detail":[{"loc","msg","type"}]}`.

OP-7 ("401 en 403 in hetzelfde foutformaat") vroeg om gelijktrekken, maar liet
de reikwijdte — met name 422 — open. Een beslissing is nodig omdat 422
structureel anders is dan de domein-/autorisatiefouten: de
CD003-/CD004-formulieren mappen `detail[].loc` rechtstreeks op het juiste
formulierveld, en OpenAPI-/FastAPI-tooling gaat uit van die vorm. Zonder
expliciet besluit ontstaat ofwel inconsistentie, ofwel onnodige herwerk-churn in
net opgeleverde formulieren.

## Besluit

### B1 — 401 naar het canonieke envelope
De auth-laag geeft 401 voortaan als
`{"fout":{"code":"NIET_GEAUTHENTICEERD","http_status":401,"bericht":…}}`, in
dezelfde exceptie-/handler-stijl als `OnvoldoendeRechten`/`NietGevonden`.
Hiermee delen **401/403/404/409** één vorm.

### B2 — 422 blijft bewust native FastAPI
422 behoudt de standaard-FastAPI-vorm `{"detail":[{"loc","msg","type"}]}`. Dit is
de **canonieke afspraak**, geen tijdelijke uitzondering. Reden: validatie is een
andere categorie dan domein-/autorisatiefouten (inherent meerdere velden,
`loc`-gebaseerd); de frontend-veldmapping en de OpenAPI-tooling hangen aan deze
vorm; en wrappen levert uitsluitend cosmetische uniformiteit op tegen reële
herwerk- en hertestkosten zonder functionele winst.

### B3 — Het foutcontract (eindstaat)
> - **`{"fout":{"code","http_status","bericht"}}`** voor **401, 403, 404, 409**
>   (auth, autorisatie, domein).
> - **`{"detail":[{"loc","msg","type"}]}`** voor **422** (FastAPI-invoervalidatie).

Dit is bewust een **twee-vormen-afspraak**, géén "één envelope overal". Generieke
clientfoutafhandeling onderscheidt op **HTTP-status** welke vorm te lezen.

### B4 — Consistentieregel voortaan
Nieuwe domein-/auth-/autorisatiefouten gebruiken altijd het `fout`-envelope;
nieuwe invoervalidatie blijft 422-native. Rauwe DB-`IntegrityError`/`HTTPException`
worden nooit ongefilterd gelekt (rollback → canonieke domeinfout).

## Gevolgen

**Positief**
- 401 is nu consistent met 403/404/409; clients kunnen één code-pad gebruiken
  voor alle niet-validatiefouten.
- Geen herwerk aan de CD003-/CD004-formulieren; OpenAPI blijft kloppen; laag
  implementatierisico.
- De afspraak is expliciet vastgelegd, zodat 422-native geen "vergeten drift"
  lijkt voor een latere lezer.

**Negatief / aandachtspunten**
- Er blijven twee foutvormen bestaan (envelope vs. `detail`-lijst). Dat is
  bewust; generieke afhandeling moet op status onderscheiden (was al zo).
- **Frontend-verificatie bij implementatie**: de sessie-verloop-flow moet op de
  **HTTP-status 401** keyen, niet op de oude body-vorm `{"detail":{"code":…}}`.

## Alternatieven overwogen

- **422 wrappen in het `fout`-envelope** — afgewezen (B2): kost herwerk aan
  net opgeleverde formulieren + OpenAPI-tooling, levert alleen cosmetische
  uniformiteit zonder functionele winst.
- **Alles native FastAPI laten (ook 401)** — afgewezen: laat 401 inconsistent met
  de reeds canonieke 403/404/409 en dwingt clients tot twee code-paden voor
  niet-validatiefouten.

## Niet in scope

- 422 wrappen in het `fout`-envelope (afgewezen — B2).
- Wijzigingen aan 403/404/409 (al canoniek). *(~~Implementatienoot CD005: het 403
  `TENANT_MISMATCH`-pad in `get_current_user` gebruikt nog de oude `detail`-vorm —
  apart opvolgpunt, buiten OP-7/CD005.~~ → **opgelost in CD009**, zie Opvolging.)*
- Nieuwe foutcodes, RLS- of rolwijzigingen (ADR-003/010 blijven leidend).
- ~~**429 / `RateLimitExceeded`**: valt buiten OP-7…~~ → **afgehecht in CD009** (was
  al canoniek), zie Opvolging.

## Opvolging (V009 — CD009)

Het foutcontract is afgehecht: de twee resterende uitzonderingen zijn nu canoniek.
- **403 `TENANT_MISMATCH`** (`get_current_user`, auth-grens — token zonder
  geldige tenant-context; géén record-level cross-tenant, dat blijft 404 per
  ADR-003) → canoniek `{"fout":{"code":"TENANT_MISMATCH","http_status":403,…}}`
  via `TenantMismatch` + handler (zelfde stijl als `NietGeauthenticeerd`).
- **429** was **al canoniek** (`rate_limit_exceeded_handler`,
  `{"fout":{"code":"RATE_LIMIT_OVERSCHREDEN","http_status":429,…}}`); bevestigd,
  ongewijzigd. Geen `Retry-After`-header aanwezig (niet toegevoegd — rate-limit-
  config valt buiten scope).

**Eindstaat foutcontract**: **401/403/404/409/429** canoniek `{"fout":{…}}`;
**422** bewust native FastAPI `{"detail":[…]}` (B2/B3).
