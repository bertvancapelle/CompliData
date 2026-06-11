/** Tests — LeverancierDetail (verwijderen; 409 IN_GEBRUIK blijft op detail). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({ api: { leveranciers: { haal: vi.fn(), verwijder: vi.fn() } } }))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import LeverancierDetail from '@modules/bwb_ontvlechting/frontend/views/LeverancierDetail.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/leveranciers', name: 'leverancier-lijst', component: { template: '<div/>' } },
      { path: '/leveranciers/:id', name: 'leverancier-detail', component: LeverancierDetail, props: true },
      { path: '/leveranciers/:id/bewerken', name: 'leverancier-bewerken', component: { template: '<div/>' } },
    ],
  })
}

async function mountDetail({ rollen = ['beheerder'] } = {}) {
  const router = maakRouter()
  await router.push('/leveranciers/l1')
  await router.isReady()
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const w = mount(LeverancierDetail, {
    props: { id: 'l1' },
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService, router], stubs: { teleport: true } },
  })
  await flushPromises()
  return { w, router }
}

beforeEach(() => {
  vi.clearAllMocks()
  api.leveranciers.haal.mockResolvedValue({ id: 'l1', naam: 'Acme BV', plaats: 'Tiel' })
})
afterEach(() => vi.restoreAllMocks())

describe('LeverancierDetail', () => {
  it('verwijdert en navigeert naar de lijst bij succes', async () => {
    api.leveranciers.verwijder.mockResolvedValueOnce(null)
    const { w, router } = await mountDetail()
    const push = vi.spyOn(router, 'push')
    await w.find('[data-testid="verwijder-knop"]').trigger('click')
    await w.find('[data-testid="verwijder-bevestig"]').trigger('click')
    await flushPromises()
    expect(api.leveranciers.verwijder).toHaveBeenCalledWith('l1')
    expect(push).toHaveBeenCalledWith({ name: 'leverancier-lijst' })
  })

  it('409 IN_GEBRUIK: blijft op detail (geen navigatie)', async () => {
    api.leveranciers.verwijder.mockRejectedValueOnce({ status: 409, code: 'IN_GEBRUIK', message: 'heeft contracten' })
    const { w, router } = await mountDetail()
    const push = vi.spyOn(router, 'push')
    await w.find('[data-testid="verwijder-knop"]').trigger('click')
    await w.find('[data-testid="verwijder-bevestig"]').trigger('click')
    await flushPromises()
    expect(api.leveranciers.verwijder).toHaveBeenCalledTimes(1)
    expect(push).not.toHaveBeenCalled() // geen navigatie weg van het detail
  })

  it('rol-gating: viewer ziet geen verwijder-knop', async () => {
    const { w } = await mountDetail({ rollen: ['viewer'] })
    expect(w.find('[data-testid="verwijder-knop"]').exists()).toBe(false)
  })
})
