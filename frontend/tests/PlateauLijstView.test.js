/** Tests — PlateauLijstView (migratielaag: lijst + aanmaken; UX-A4-1). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: { plateaus: { lijst: vi.fn(), maak: vi.fn() } },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import PlateauLijstView from '@/views/migratie/PlateauLijstView.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/migratie/plateaus', name: 'plateau-lijst', component: PlateauLijstView },
      { path: '/migratie/plateaus/:id', name: 'plateau-detail', component: { template: '<div/>' }, props: true },
    ],
  })
}

async function mountLijst({ rollen = ['beheerder'] } = {}) {
  const router = maakRouter()
  await router.push('/migratie/plateaus')
  await router.isReady()
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const w = mount(PlateauLijstView, {
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService, router], stubs: { teleport: true } },
  })
  await flushPromises()
  return { w, router }
}

beforeEach(() => {
  vi.clearAllMocks()
  api.plateaus.lijst.mockResolvedValue({ items: [{ id: 'pl1', naam: 'Huidig', toelichting: null }], volgende_cursor: null })
})
afterEach(() => vi.restoreAllMocks())

describe('PlateauLijstView', () => {
  it('toont de plateaus + de "+ Nieuw plateau"-knop voor beheerder', async () => {
    const { w } = await mountLijst()
    expect(w.text()).toContain('Huidig')
    expect(w.find('[data-testid="plateau-nieuw"]').exists()).toBe(true)
  })

  it('viewer ziet geen "+ Nieuw plateau"-knop (rol-gating)', async () => {
    const { w } = await mountLijst({ rollen: ['viewer'] })
    expect(w.find('[data-testid="plateau-nieuw"]').exists()).toBe(false)
  })

  it('naam leeg ⇒ validatiefout, geen API-call', async () => {
    const { w } = await mountLijst()
    await w.find('[data-testid="plateau-nieuw"]').trigger('click')
    await w.find('[data-testid="plateau-nieuw-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="pl-fout-naam"]').exists()).toBe(true)
    expect(api.plateaus.maak).not.toHaveBeenCalled()
  })

  it('aanmaken roept maak aan en navigeert naar het nieuwe plateau-detail', async () => {
    api.plateaus.maak.mockResolvedValueOnce({ id: 'pl9' })
    const { w, router } = await mountLijst()
    await w.find('[data-testid="plateau-nieuw"]').trigger('click')
    await w.find('[data-testid="pl-naam"]').setValue('Doel 2027')
    await w.find('[data-testid="pl-toelichting"]').setValue('Eindbeeld')
    await w.find('[data-testid="plateau-nieuw-form"]').trigger('submit')
    await flushPromises()
    expect(api.plateaus.maak).toHaveBeenCalledWith({ naam: 'Doel 2027', toelichting: 'Eindbeeld' })
    expect(router.currentRoute.value.name).toBe('plateau-detail')
    expect(router.currentRoute.value.params.id).toBe('pl9')
  })

  it('lege lijst toont een actie-uitleg voor wie mag aanmaken', async () => {
    api.plateaus.lijst.mockResolvedValueOnce({ items: [], volgende_cursor: null })
    const { w } = await mountLijst()
    const leeg = w.find('[data-testid="plateau-lijst-leeg"]')
    expect(leeg.exists()).toBe(true)
    expect(leeg.text()).toContain('+ Nieuw plateau')
  })
})
