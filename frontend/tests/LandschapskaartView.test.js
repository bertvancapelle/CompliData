/** Tests — LandschapskaartView v3 (ADR-025, Cytoscape; drie modi + zoek/filter/set/detail). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'

// Cytoscape gemockt (via de frontend-wrapper): de graaf-rendering is een side-effect;
// de panelen zijn de testbare laag.
vi.mock('@/composables/cytoscape', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    elements: () => ({ remove: vi.fn(), unselect: vi.fn() }),
    getElementById: () => ({ length: 0, select: vi.fn() }),
    animate: vi.fn(),
    zoom: () => 1,
    add: vi.fn(),
    layout: () => ({ run: vi.fn() }),
    resize: vi.fn(),
    fit: vi.fn(),
    destroy: vi.fn(),
  })),
}))
vi.mock('@/api', () => ({ api: { landschapskaart: { haalGrafdata: vi.fn() } } }))

import cytoscape from '@/composables/cytoscape'
import { api } from '@/api'
import LandschapskaartView from '@modules/bwb_ontvlechting/frontend/views/LandschapskaartView.vue'

const GRAF = () => ({
  nodes: [
    { id: 'a1', naam: 'Zaaksysteem', element_type: 'applicatie', laag: 'application', lifecycle_status: 'migratieklaar', domein: 'applicatie', hosting_model: 'saas', leverancier_naam: 'SaaS BV', blokkades_open: 0 },
    { id: 'a2', naam: 'Documentbeheer', element_type: 'applicatie', laag: 'application', lifecycle_status: 'geblokkeerd', domein: 'applicatie', hosting_model: 'on_premise', leverancier_naam: null, blokkades_open: 1 },
    { id: 'p1', naam: 'Org', element_type: 'partij', laag: 'business', soort: 'organisatie', blokkades_open: 0 },
    { id: 'k1', naam: 'Contract X', element_type: 'contract', laag: 'business', blokkades_open: 0 },
  ],
  edges: [{ bron_id: 'a1', doel_id: 'a2', relatietype: 'flow', label: 'koppeling', ring: 'applicaties' }],
})

async function mountView({ query = '' } = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div/>' } },
      { path: '/landschapskaart', name: 'landschapskaart', component: { template: '<div/>' } },
      { path: '/applicaties/:id', name: 'applicatie-detail', component: { template: '<div/>' } },
    ],
  })
  await router.push(`/landschapskaart${query}`)
  await router.isReady()
  const pushSpy = vi.spyOn(router, 'push')
  const w = mount(LandschapskaartView, { global: { plugins: [router] } })
  await flushPromises()
  return { w, pushSpy }
}

beforeEach(() => {
  vi.clearAllMocks()
  api.landschapskaart.haalGrafdata.mockResolvedValue(GRAF())
})
afterEach(() => vi.restoreAllMocks())

describe('LandschapskaartView v3', () => {
  it('rendert in Ego-modus en initialiseert Cytoscape', async () => {
    const { w } = await mountView()
    expect(cytoscape).toHaveBeenCalled()
    expect(w.find('[data-testid="lk-canvas"]').exists()).toBe(true)
    expect(w.find('[data-testid="lk-modus-ego"]').attributes('aria-pressed')).toBe('true')
    // resultatenlijst toont ALLEEN applicaties (a1, a2) — niet de partij/contract.
    expect(w.findAll('[data-testid^="lk-res-naam-"]').length).toBe(2)
    expect(w.find('[data-testid="lk-res-naam-p1"]').exists()).toBe(false)
    expect(w.find('[data-testid="lk-res-naam-k1"]').exists()).toBe(false)
  })

  it('zoekfilter vermindert de zichtbare resultaten', async () => {
    const { w } = await mountView()
    await w.find('[data-testid="lk-zoek"]').setValue('zaak')
    await flushPromises()
    expect(w.find('[data-testid="lk-res-naam-a1"]').exists()).toBe(true)
    expect(w.find('[data-testid="lk-res-naam-a2"]').exists()).toBe(false)
    expect(w.findAll('[data-testid^="lk-res-naam-"]').length).toBe(1)
  })

  it('Impact-modus telt set/raakvlakken/grensoverschrijdend', async () => {
    const { w } = await mountView()
    await w.find('[data-testid="lk-modus-impact"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-testid="impact-samenvatting"]').text()).toBe('0 in set · 0 raakvlakken · 0 grensoverschrijdende koppelingen')
    await w.find('[data-testid="lk-res-set-a1"]').trigger('click') // a1 in de set
    await flushPromises()
    // flow a1→a2: a2 wordt raakvlak, koppeling grensoverschrijdend.
    expect(w.find('[data-testid="impact-samenvatting"]').text()).toBe('1 in set · 1 raakvlakken · 1 grensoverschrijdende koppelingen')
  })

  it('Geheel-model toont direct alle nodes en vult de set met alle applicaties (Fix 1)', async () => {
    const { w } = await mountView()
    await w.find('[data-testid="lk-modus-geheel"]').trigger('click')
    await flushPromises()
    // Volledig landschap meteen zichtbaar (alle 4 nodes), en de actieve set bevat de 2 applicaties.
    expect(w.find('[data-testid="lk-zichtbaar-aantal"]').text()).toContain('4 nodes')
    expect(w.find('[data-testid="lk-rechts"]').text()).toContain('Actieve set (2)')
  })

  it('node-klik (resultaatrij) toont het detail-paneel', async () => {
    const { w } = await mountView()
    expect(w.find('[data-testid="lk-detail-leeg"]').exists()).toBe(true)
    await w.find('[data-testid="lk-res-naam-a2"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-testid="lk-detail-naam"]').text()).toBe('Documentbeheer')
  })

  it('"Open applicatie →" navigeert naar het applicatie-detail', async () => {
    const { w, pushSpy } = await mountView()
    await w.find('[data-testid="lk-res-naam-a1"]').trigger('click')
    await flushPromises()
    await w.find('[data-testid="lk-detail-open"]').trigger('click')
    expect(pushSpy).toHaveBeenCalledWith({ name: 'applicatie-detail', params: { id: 'a1' } })
  })

  it('"Voeg alle gefilterde toe" vult de actieve set', async () => {
    const { w } = await mountView()
    await w.find('[data-testid="lk-voeg-alle"]').trigger('click')
    await flushPromises()
    // alleen de twee applicaties komen in de set (partij/contract zijn niet selecteerbaar).
    expect(w.find('[data-testid="lk-rechts"]').text()).toContain('Actieve set (2)')
  })

  it('Fix 3: klik op een actieve-set-item selecteert de node (detail-paneel)', async () => {
    const { w } = await mountView()
    await w.find('[data-testid="lk-res-set-a1"]').trigger('click') // a1 in de set
    await flushPromises()
    await w.find('[data-testid="lk-set-a1"]').find('button').trigger('click') // klik het set-item (naam)
    await flushPromises()
    expect(w.find('[data-testid="lk-detail-naam"]').text()).toBe('Zaaksysteem')
  })

  it('deep-link ?center=<id>&modus=ego zet de modus en de actieve set (ADR-025)', async () => {
    const { w } = await mountView({ query: '?center=a1&modus=ego' })
    expect(w.find('[data-testid="lk-modus-ego"]').attributes('aria-pressed')).toBe('true')
    // de center-applicatie staat in de actieve set en is het detail.
    expect(w.find('[data-testid="lk-rechts"]').text()).toContain('Actieve set (1)')
    expect(w.find('[data-testid="lk-detail-naam"]').text()).toBe('Zaaksysteem')
  })

  it('toont het blokkade-icoon op een node met open blokkades', async () => {
    const { w } = await mountView()
    expect(w.find('[data-testid="lk-res-blok-a2"]').exists()).toBe(true)
    expect(w.find('[data-testid="lk-res-blok-a1"]').exists()).toBe(false)
  })
})
