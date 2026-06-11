/** Tests — LeverancierFormulier (naam verplicht client-side; 422-mapping). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: { leveranciers: { maak: vi.fn(), haal: vi.fn(), werkBij: vi.fn() } },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import LeverancierFormulier from '@modules/bwb_ontvlechting/frontend/views/LeverancierFormulier.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/leveranciers', name: 'leverancier-lijst', component: { template: '<div/>' } },
      { path: '/leveranciers/nieuw', name: 'leverancier-nieuw', component: LeverancierFormulier },
      { path: '/leveranciers/:id', name: 'leverancier-detail', component: { template: '<div/>' } },
    ],
  })
}

async function mountForm({ id = null } = {}) {
  const router = maakRouter()
  await router.push('/leveranciers/nieuw')
  await router.isReady()
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: ['medewerker'] }
  const w = mount(LeverancierFormulier, {
    props: { id },
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService, router] },
  })
  await flushPromises()
  return { w, router }
}

beforeEach(() => vi.clearAllMocks())
afterEach(() => vi.restoreAllMocks())

describe('LeverancierFormulier', () => {
  it('weigert lege naam client-side (geen API-call)', async () => {
    const { w } = await mountForm()
    await w.find('[data-testid="leverancier-form"]').trigger('submit')
    expect(w.find('[data-testid="fout-naam"]').exists()).toBe(true)
    expect(api.leveranciers.maak).not.toHaveBeenCalled()
  })

  it('maakt aan met geldige naam (overige velden null) en navigeert naar detail', async () => {
    api.leveranciers.maak.mockResolvedValueOnce({ id: 'l1' })
    const { w, router } = await mountForm()
    await w.find('[data-testid="veld-naam"]').setValue('Acme BV')
    await w.find('[data-testid="veld-plaats"]').setValue('Tiel')
    await w.find('[data-testid="leverancier-form"]').trigger('submit')
    await flushPromises()
    expect(api.leveranciers.maak).toHaveBeenCalledTimes(1)
    const payload = api.leveranciers.maak.mock.calls[0][0]
    expect(payload).toMatchObject({ naam: 'Acme BV', plaats: 'Tiel', email: null })
    expect(router.currentRoute.value.name).toBe('leverancier-detail')
  })

  it('zet 422-veldfout op het juiste veld', async () => {
    api.leveranciers.maak.mockRejectedValueOnce({
      status: 422,
      detail: [{ loc: ['body', 'postcode'], msg: 'Maximaal 20 tekens.' }],
    })
    const { w } = await mountForm()
    await w.find('[data-testid="veld-naam"]').setValue('Acme')
    await w.find('[data-testid="leverancier-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="fout-postcode"]').text()).toContain('Maximaal 20')
  })
})
