/**
 * Tests — PlaatsingSignalenView (consistentie-signalering, F-3 stap 2).
 * api gemockt; render van de signalenlijst met leesbare signaalteksten + de lege staat.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

vi.mock('@/api', () => ({
  api: { signalen: { plaatsing: vi.fn() } },
}))

import { api } from '@/api'
import PlaatsingSignalenView from '@/views/PlaatsingSignalenView.vue'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div/>' } },
      { path: '/componenten/:id', name: 'component-detail', component: { template: '<div/>' } },
    ],
  })
}

const _items = () => [
  {
    component_id: 'a1', naam: 'Zaaksysteem', componenttype: 'applicatie',
    signaal: 'beoordeeld_niet_vastgelegd', score: 'ja', draait_op: false,
    reden: 'De plaatsingsvraag is positief beoordeeld, maar er is geen draait_op-relatie vastgelegd.',
  },
  {
    component_id: 'a2', naam: 'Documentbeheer', componenttype: 'applicatie',
    signaal: 'vastgelegd_niet_beoordeeld', score: null, draait_op: true,
    reden: 'Er is een draait_op-relatie vastgelegd, maar de plaatsingsvraag is niet positief beoordeeld.',
  },
]

async function mountView() {
  const router = maakRouter()
  await router.push('/')
  await router.isReady()
  const w = mount(PlaatsingSignalenView, {
    global: { plugins: [createPinia(), [PrimeVue, { unstyled: true }], router] },
  })
  await flushPromises()
  return w
}

afterEach(() => vi.restoreAllMocks())
beforeEach(() => vi.clearAllMocks())

describe('PlaatsingSignalenView', () => {
  it('rendert de signalen met leesbare signaalteksten', async () => {
    api.signalen.plaatsing.mockResolvedValue(_items())
    const w = await mountView()
    const tekst = w.find('[data-testid="signalen-tabel"]').text()
    expect(tekst).toContain('Zaaksysteem')
    expect(tekst).toContain('Documentbeheer')
    // Leesbare teksten (geen jargon-sleutels).
    expect(w.find('[data-testid="signaal-type-a1"]').text()).toBe('Plaatsing beoordeeld maar niet vastgelegd')
    expect(w.find('[data-testid="signaal-type-a2"]').text()).toBe('Plaatsing vastgelegd maar niet beoordeeld')
    expect(tekst).not.toContain('beoordeeld_niet_vastgelegd') // sleutel niet zichtbaar
  })

  it('B2: component-naam linkt door naar het component-detail', async () => {
    api.signalen.plaatsing.mockResolvedValue(_items())
    const w = await mountView()
    expect(w.find('[data-testid="signaal-link-a1"]').attributes('href')).toContain('/componenten/a1')
    expect(w.find('[data-testid="signaal-link-a2"]').attributes('href')).toContain('/componenten/a2')
  })

  it('B3: de intro toont geen datamodel-term "draait_op-relatie"', async () => {
    api.signalen.plaatsing.mockResolvedValue([])
    const w = await mountView()
    expect(w.text()).not.toContain('draait_op-relatie')
  })

  it('toont de lege staat als er geen signalen zijn', async () => {
    api.signalen.plaatsing.mockResolvedValue([])
    const w = await mountView()
    expect(w.find('[data-testid="signalen-leeg"]').exists()).toBe(true)
    expect(w.find('[data-testid="signalen-tabel"]').exists()).toBe(false)
  })

  it('toont een foutmelding bij een API-fout', async () => {
    api.signalen.plaatsing.mockRejectedValue(new Error('kapot'))
    const w = await mountView()
    expect(w.find('[data-testid="signalen-fout"]').exists()).toBe(true)
  })
})
