/** Tests — SignaleringView (ADR-035 Slice 1): twee tabs; Registratiegaten laadt de gaten. */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('@/api', () => ({
  api: {
    signalering: { registratiegaten: vi.fn() },
    signalen: { plaatsing: vi.fn() }, // PlaatsingSignalenView (ingebedde tab) roept dit op mount aan
  },
}))

import { api } from '@/api'
import SignaleringView from '@/views/SignaleringView.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div/>' } },
      { path: '/c/:id', name: 'component-detail', component: { template: '<div/>' } },
    ],
  })
}

async function mountView() {
  const router = maakRouter()
  await router.push('/')
  await router.isReady()
  const w = mount(SignaleringView, { global: { plugins: [router] } })
  await flushPromises()
  return w
}

beforeEach(() => {
  vi.clearAllMocks()
  api.signalen.plaatsing.mockResolvedValue([])
  api.signalering.registratiegaten.mockResolvedValue({
    component_zonder_eigenaar: [{ id: 'c1', naam: 'Zaaksysteem', lifecycle_status: 'concept', signaal: 'component_zonder_eigenaar', niveau: 'kritiek' }],
    component_zonder_verantwoordelijke: [],
  })
})
afterEach(() => vi.restoreAllMocks())

describe('SignaleringView', () => {
  it('toont twee tabs en laadt de registratiegaten op mount', async () => {
    const w = await mountView()
    expect(w.find('[data-testid="sig-tab-registratiegaten"]').exists()).toBe(true)
    expect(w.find('[data-testid="sig-tab-plaatsing"]').exists()).toBe(true)
    expect(api.signalering.registratiegaten).toHaveBeenCalled()
    expect(w.find('[data-testid="sig-eigenaar-c1"]').exists()).toBe(true)
    expect(w.find('[data-testid="sig-eigenaar-c1"]').text()).toContain('Zaaksysteem')
  })

  it('lege gaten → groene "geen registratiegaten"-staat', async () => {
    api.signalering.registratiegaten.mockResolvedValue({ component_zonder_eigenaar: [], component_zonder_verantwoordelijke: [] })
    const w = await mountView()
    expect(w.find('[data-testid="sig-leeg"]').exists()).toBe(true)
  })

  it('tab "Plaatsing" toont de bestaande plaatsingssignalen-view (ingebed)', async () => {
    const w = await mountView()
    await w.find('[data-testid="sig-tab-plaatsing"]').trigger('click')
    expect(w.find('[data-testid="sig-panel-plaatsing"]').exists()).toBe(true)
    expect(api.signalen.plaatsing).toHaveBeenCalled() // ingebedde view laadde
  })
})
