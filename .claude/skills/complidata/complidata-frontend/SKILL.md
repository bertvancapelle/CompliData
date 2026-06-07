---
name: complidata-frontend
description: Frontend-patronen voor CompliData (Vue 3, PrimeVue Unstyled, Tailwind v4). Beschrijft de werkelijke V003-staat (login + app-shell + module-views).
stack: Vue 3, Vite, PrimeVue Unstyled, Tailwind CSS v4, Pinia, vue-router, vitest
bijgewerkt: V003
---

# CompliData Frontend Skill

## PrimeVue Unstyled + PassThrough presets

```javascript
// src/main.js
app.use(createPinia())
app.use(router)
app.use(PrimeVue, { unstyled: true, pt: presets })   // pt = src/presets/index.js
app.use(ToastService)
```

Elke gebruikte PrimeVue-component vereist een preset in `src/presets/` (anders
rendert hij leeg in unstyled-mode). Aanwezig: Button, DataTable, Dialog, Drawer,
InputText, Popover, Tag, Textarea, Toast (+ `index.js`). Column heeft géén eigen
preset nodig (de DataTable-preset stuurt header/body/empty).

## Design-tokens + styling

- Altijd de **`--cd-`-prefix** (uit `src/themes/base.css`). Geen `<style>`-blokken;
  uitsluitend Tailwind-utilities + `--cd-`-tokens. `assets/main.css` importeert
  Tailwind v4 + `base.css` + globale resets/utilities (o.a. `.card`).
- Tailwind arbitrary aria-variant voor de actieve nav-link:
  `aria-[current=page]:bg-[var(--cd-color-accent)]`.

## Frontend-module-loading (Optie A — V003)

Module-frontendcode staat **buiten** de vite-root in
`modules/<module>/frontend/` (views/, labels.js). Geregeld via vite-config:

```javascript
// frontend/vite.config.js
resolve: { alias: {
  '@':        fileURLToPath(new URL('./src', import.meta.url)),
  '@modules': fileURLToPath(new URL('../modules', import.meta.url)),  // generiek
}},
server: { fs: { allow: [frontendDir, modulesDir] } },   // strak gescoopt, niet kale ..
```

- De centrale router importeert een module-view via `@modules/...` en registreert
  hem als **child onder `AppLayout`** (erft `requiresAuth` via de meta-merge → guard
  ongewijzigd). Statische subpaden (`/nieuw`) vóór `/:id`; `props: true` voor
  id-routes.

### Cross-root-barrels (VERPLICHT patroon voor module-views)

`node_modules` woont in `frontend/`; module-views buiten de root kunnen bare deps
(`primevue/*`, `vue-router`) niet resolven. Importeer gedeelde deps daarom via
platform-barrels:

```javascript
import { DataTable, Column, Tag, Button, Dialog, InputText, Textarea, useToast } from '@/primevue'
import { useRouter, useRoute } from '@/composables/router'
import { api } from '@/api'
```

Breid `src/primevue.js` / `src/composables/router.js` uit zodra een view een extra
component/composable nodig heeft. (`vue` zelf resolvet wél cross-root — vite dedupet
het.) Route-params bij voorkeur via `props: true`, niet `useRoute`.

## App-shell (AppLayout) + router-nesting

```
src/layouts/AppLayout.vue   — topbar (app-naam, gebruiker-e-mail, uitlog-knop) +
                              inklapbare sidebar (nav) + hoofd-<router-view> + <Toast/>
```

- Sidebar-toggle: `aria-expanded`/`aria-controls`; voorkeur optioneel in
  `localStorage` (`cd-sidebar-ingeklapt`, niet-gevoelig, try/catch).
- Router: geauthenticeerde routes als children onder `AppLayout`;
  `login`/`auth-callback`/`verboden` standalone (`meta.public`). De guard
  (`store/auth.js` + `router/index.js`) blijft ongewijzigd.
- Uitloggen: `auth.logout()` (wist `cd_session`, redirect `/login`). **OP-4**:
  geen Keycloak-SSO-logout (buiten scope; in code gedocumenteerd).

## api.js fetch-wrapper

```javascript
// src/api.js — BASE='/api/v1', credentials:'include' (httpOnly cookie)
// 401 -> throw 'NIET_GEAUTHENTICEERD'; 204 -> null (DELETE);
// fout verrijkt met { status, code, detail } voor 403/404/409/422-mapping.
api.applicaties.{lijst({limit,after}), haal(id), maak(data), werkBij(id,data),
                 startInventarisatie(id), verwijder(id), opties()}
```

Voeg per entiteit platte methodes toe via de interne `request()`-helper (geen
generieke get/post).

## Data-view-patroon (lijst)

- PrimeVue `DataTable` + `Column`; **keyset-cursor-paginering** met "Meer laden"
  (`volgende_cursor`; `null` = einde). Lifecycle/status als `Tag` (severity-map in
  `labels.js`). Lege-/laad-/foutstatus; fout in `role="alert"`. Detail-navigatie
  via een toetsenbord-toegankelijke `<router-link>` op de naam.

## Formulier-patroon

- Dropdowns uit het backend **opties-endpoint** (`applicaties.opties()`) +
  per-module `labels.js` (NL-labels met **humanize-fallback** — een nieuwe
  backend-waarde verschijnt direct, hooguit generiek gelabeld). Native `<select>`
  (geen Select-preset).
- Clientvalidatie **spiegelt de backend-schemas** (naam verplicht, vrije-tekst-/
  lengtegrenzen, enums verplicht). **422-veldfouten** van de backend
  (`{detail:[{loc:[...,veld],msg}]}`) op het juiste veld zetten.
- Succes/fout via `Toast`; fout-mapping 403→geen rechten, 404→niet gevonden,
  409→conflict, 422→veldfouten, 401→bestaande sessie-flow.
- Toegankelijk: `label/for`, `aria-invalid`, `aria-describedby`, focusbeheer.

## Rol-gating = affordance (backend handhaaft)

```javascript
// src/store/auth.js — hasRole IS functioneel post-ADR-010 (rollen uit /auth/me)
const auth = useAuthStore()
auth.hasRole('medewerker', 'beheerder')   // toont/verbergt knoppen
```

De UI verbergt alleen knoppen; de **backend** handhaaft via `vereist_permissie`.
Vang een toch-403 netjes af (Toast). Nooit tokens in `localStorage` (httpOnly).

## Login-patroon (LoginView)

- Launch-page met één knop → **volledige** browser-redirect:
  `window.location.assign('/api/v1/auth/login')` (geen `fetch`, geen in-app
  wachtwoordveld). `next` alleen meesturen bij een same-origin relatief pad
  (backend hervalideert). `?sessie_verlopen=1` → inline `role="alert"`.
- Na login zet de backend `cd_session` en redirect naar `next` (default `/`); de
  router-guard zet de gebruiker door.

## Testopzet (vitest)

- Poorten: `vite build` + `vitest` (geen eslint/type-check).
- Module-view-tests staan onder **`frontend/tests/`** (binnen de vitest-root;
  vitest scant niet buiten `frontend/`) en importeren de view via `@modules`.
- Mock `@/api` met `vi.mock`; mount met `[pinia, [PrimeVue,{unstyled:true}],
  ToastService, router]`. PrimeVue `Dialog` teleporteert naar body → gebruik
  `global.stubs: { teleport: true }` zodat `find()` de inhoud ziet. `window.location`
  via `vi.stubGlobal('location', { assign: vi.fn() })`.

## Openstaande punten (V003)

| Onderdeel | Status |
|---|---|
| `tenantSlug`-getter | Leest `user.tenant_slug`, maar `/auth/me` geeft `tenant_id` → altijd null. Fix bij theming. |
| Bundle >500 kB | DataTable; route-level lazy-loading als optimalisatie. |
| Per-tenant thema's | `useTheme` aanwezig; nog geen tenant-thema's. |
| Login/SSO-logout | OP-3 (refresh) / OP-4 (RP-logout) open. |
