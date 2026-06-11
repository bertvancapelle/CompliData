/** Tests — LeverancierLijst (module-view via @modules). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

vi.mock('@/api', () => ({ api: { leveranciers: { lijst: vi.fn() } } }))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import LeverancierLijst from '@modules/bwb_ontvlechting/frontend/views/LeverancierLijst.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/leveranciers', name: 'leverancier-lijst', component: LeverancierLijst },
      { path: '/leveranciers/nieuw', name: 'leverancier-nieuw', component: { template: '<div/>' } },
      { path: '/leveranciers/:id', name: 'leverancier-detail', component: { template: '<div/>' } },
    ],
  })
}

async function mountLijst({ rollen = ['medewerker'] } = {}) {
  const router = maakRouter()
  await router.push('/leveranciers')
  await router.isReady()
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const w = mount(LeverancierLijst, { global: { plugins: [pinia, [PrimeVue, { unstyled: true }], router] } })
  await flushPromises()
  return w
}

const _lev = (naam, id) => ({ id, naam, plaats: 'Tiel', contactpersoon: 'J. Jansen' })

beforeEach(() => vi.clearAllMocks())
afterEach(() => vi.restoreAllMocks())

describe('LeverancierLijst', () => {
  it('rendert de geladen leveranciers', async () => {
    api.leveranciers.lijst.mockResolvedValueOnce({ items: [_lev('Acme BV', 'l1'), _lev('Globex', 'l2')], volgende_cursor: null })
    const w = await mountLijst()
    expect(w.text()).toContain('Acme BV')
    expect(w.text()).toContain('Globex')
  })

  it('"Meer laden" pagineert met de cursor', async () => {
    api.leveranciers.lijst
      .mockResolvedValueOnce({ items: [_lev('Eerste', 'l1')], volgende_cursor: 'cur-1' })
      .mockResolvedValueOnce({ items: [_lev('Tweede', 'l2')], volgende_cursor: null })
    const w = await mountLijst()
    await w.find('[data-testid="meer-laden"]').trigger('click')
    await flushPromises()
    expect(api.leveranciers.lijst).toHaveBeenLastCalledWith({ limit: 25, after: 'cur-1' })
    expect(w.find('[data-testid="meer-laden"]').exists()).toBe(false)
  })

  it('linkt elke rij naar de detail-route', async () => {
    api.leveranciers.lijst.mockResolvedValueOnce({ items: [_lev('Acme', 'l-42')], volgende_cursor: null })
    const w = await mountLijst()
    expect(w.find('[data-testid="rij-link"]').attributes('href')).toContain('/leveranciers/l-42')
  })

  it('lege status zonder items', async () => {
    api.leveranciers.lijst.mockResolvedValueOnce({ items: [], volgende_cursor: null })
    expect((await mountLijst()).find('[data-testid="lijst-leeg"]').exists()).toBe(true)
  })

  it('foutmelding (role=alert) bij API-fout', async () => {
    api.leveranciers.lijst.mockRejectedValueOnce(new Error('Netwerkfout'))
    const w = await mountLijst()
    expect(w.find('[data-testid="lijst-fout"]').attributes('role')).toBe('alert')
  })

  it('rol-gating: aanmaak-knop alleen voor medewerker+', async () => {
    api.leveranciers.lijst.mockResolvedValue({ items: [], volgende_cursor: null })
    expect((await mountLijst({ rollen: ['medewerker'] })).find('[data-testid="nieuwe-leverancier"]').exists()).toBe(true)
    expect((await mountLijst({ rollen: ['viewer'] })).find('[data-testid="nieuwe-leverancier"]').exists()).toBe(false)
  })
})
