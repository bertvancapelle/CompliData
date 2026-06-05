---
name: complidata-frontend
description: Frontend-patronen voor CompliData (Vue 3, PrimeVue Unstyled, Tailwind v4). Beschrijft de werkelijke V001-staat.
stack: Vue 3, Vite, PrimeVue Unstyled, Tailwind CSS v4, Pinia, vue-router
bijgewerkt: V001
---

# CompliData Frontend Skill

## PrimeVue Unstyled + PassThrough presets

```javascript
// src/main.js
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import presets from './presets'

app.use(createPinia())
app.use(router)
app.use(PrimeVue, { unstyled: true, pt: presets })
app.use(ToastService)
```

10 presets in `src/presets/`: Button, DataTable, Dialog, Drawer, InputText,
Popover, Tag, Textarea, Toast + `index.js`. Elke gebruikte PrimeVue-component
vereist een preset (anders rendert hij leeg in unstyled-mode).

## Design token-prefix: --cd-

```css
/* src/themes/base.css — 45 tokens */
:root {
  --cd-color-primary: #1B4B82;
  --cd-color-text: #1A1A2E;
  --cd-space-md: 16px;
}
```

Gebruik ALTIJD de `--cd-`-prefix.

## Styling-regel

Geen `<style>`-blokken in views/componenten. Uitsluitend Tailwind
utility-klassen + `--cd-`-tokens. `assets/main.css` importeert Tailwind v4
(`@import "tailwindcss";`) + `themes/base.css` + base resets.

## useTheme.js

```javascript
// src/composables/useTheme.js
// Laadt /themes/{tenantSlug}.css dynamisch per tenant.
// V001: nog geen tenant-thema's aanwezig — base.css levert de defaults.
import { useTheme } from '../composables/useTheme'
```

## api.js fetch-wrapper

```javascript
// src/api.js — BASE = '/api/v1', credentials: 'include' (httpOnly cookie)
// Foutformaat: { fout: { code, http_status, bericht } }; 401 -> 'NIET_GEAUTHENTICEERD'
import { api } from './api'
const gebruiker = await api.me()      // GET /api/v1/auth/me
await api.logout()                    // POST /api/v1/auth/logout
```

Voeg nieuwe endpoints toe als platte methodes op het `api`-object via de
interne `request()`-helper. Geen generieke `api.get/post`.

## Auth store (Pinia)

```javascript
// src/store/auth.js — httpOnly cookie-sessie, NOOIT localStorage
const auth = useAuthStore()
await auth.fetchSession()     // fetch /api/v1/auth/me
auth.isAuthenticated         // getter
auth.hasRole('...')          // V001: altijd false tot ADR-010
```

## Router-guard

```javascript
router.beforeEach(async (to) => {
  if (to.meta.public) return true
  const auth = useAuthStore()
  await auth.fetchSession()
  if (!auth.isAuthenticated) return { name: 'login', query: { sessie_verlopen: '1' } }
  if (to.meta.roles?.length && !auth.hasRole(...to.meta.roles)) return { name: 'verboden' }
  return true
})
```

De router gebruikt nu placeholder-componenten; module-views worden onder
`modules/<module>/frontend` toegevoegd en hier geregistreerd.

## Openstaande punten V001

| Onderdeel | Status |
|---|---|
| Module-views | Nog niet aangemaakt (placeholders in router) |
| Branding-tokens | Placeholder-palet — aanpassen bij definitieve huisstijl |
| `hasRole()` | Altijd false — volgt uit ADR-010 |
| Login/callback PKCE | Nog niet geïmplementeerd — ADR-002 |
