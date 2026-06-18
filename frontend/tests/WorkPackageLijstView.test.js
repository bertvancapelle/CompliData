/** Tests — WorkPackageLijstView (migratielaag: lijst + aanmaken; UX-A4-2). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: { workPackages: { lijst: vi.fn(), maak: vi.fn() } },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import WorkPackageLijstView from '@/views/migratie/WorkPackageLijstView.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/migratie/werkpakketten', name: 'work-package-lijst', component: WorkPackageLijstView },
      { path: '/migratie/werkpakketten/:id', name: 'work-package-detail', component: { template: '<div/>' }, props: true },
    ],
  })
}

async function mountLijst({ rollen = ['beheerder'] } = {}) {
  const router = maakRouter()
  await router.push('/migratie/werkpakketten')
  await router.isReady()
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const w = mount(WorkPackageLijstView, {
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService, router], stubs: { teleport: true } },
  })
  await flushPromises()
  return { w, router }
}

async function kiesZoek(w, prefix, id) {
  await w.find(`[data-testid="${prefix}-input"]`).trigger('focus')
  await flushPromises()
  await w.find(`[data-testid="${prefix}-optie-${id}"]`).trigger('mousedown')
  await flushPromises()
}

beforeEach(() => {
  vi.clearAllMocks()
  api.workPackages.lijst.mockResolvedValue({
    items: [{ id: 'w1', naam: 'Financieel domein', bovenliggend_id: null, toelichting: null }],
    volgende_cursor: null,
  })
})
afterEach(() => vi.restoreAllMocks())

describe('WorkPackageLijstView', () => {
  it('toont de werkpakketten + "+ Nieuw werkpakket" voor beheerder', async () => {
    const { w } = await mountLijst()
    expect(w.text()).toContain('Financieel domein')
    expect(w.find('[data-testid="wp-nieuw"]').exists()).toBe(true)
  })

  it('viewer ziet geen "+ Nieuw werkpakket" (rol-gating)', async () => {
    const { w } = await mountLijst({ rollen: ['viewer'] })
    expect(w.find('[data-testid="wp-nieuw"]').exists()).toBe(false)
  })

  it('naam leeg ⇒ validatiefout, geen API-call', async () => {
    const { w } = await mountLijst()
    await w.find('[data-testid="wp-nieuw"]').trigger('click')
    await w.find('[data-testid="wp-nieuw-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="wp-fout-naam"]').exists()).toBe(true)
    expect(api.workPackages.maak).not.toHaveBeenCalled()
  })

  it('aanmaken (top-niveau) roept maak aan en navigeert naar het detail', async () => {
    api.workPackages.maak.mockResolvedValueOnce({ id: 'w9' })
    const { w, router } = await mountLijst()
    await w.find('[data-testid="wp-nieuw"]').trigger('click')
    await w.find('[data-testid="wp-naam"]').setValue('Datadomein')
    await w.find('[data-testid="wp-nieuw-form"]').trigger('submit')
    await flushPromises()
    expect(api.workPackages.maak).toHaveBeenCalledWith({ naam: 'Datadomein', toelichting: null, bovenliggend_id: null })
    expect(router.currentRoute.value.params.id).toBe('w9')
  })

  it('aanmaken als sub-werkpakket stuurt het gekozen bovenliggend mee', async () => {
    api.workPackages.maak.mockResolvedValueOnce({ id: 'w9' })
    const { w } = await mountLijst()
    await w.find('[data-testid="wp-nieuw"]').trigger('click')
    await w.find('[data-testid="wp-naam"]').setValue('Oracle-DB overzetten')
    await kiesZoek(w, 'wp-veld-bovenliggend', 'w1')
    await w.find('[data-testid="wp-nieuw-form"]').trigger('submit')
    await flushPromises()
    expect(api.workPackages.maak).toHaveBeenCalledWith({ naam: 'Oracle-DB overzetten', toelichting: null, bovenliggend_id: 'w1' })
  })

  it('lege lijst toont een actie-uitleg voor wie mag aanmaken', async () => {
    api.workPackages.lijst.mockResolvedValueOnce({ items: [], volgende_cursor: null })
    const { w } = await mountLijst()
    const leeg = w.find('[data-testid="wp-lijst-leeg"]')
    expect(leeg.exists()).toBe(true)
    expect(leeg.text()).toContain('+ Nieuw werkpakket')
  })
})
