/**
 * Tests — Landschapskaart popups + fullscreen (klik op koppeling/knoop, dubbelklik =
 * hercentreren, fullscreen-overlay met staat-behoud). Cytoscape gemockt; de popup-/
 * fullscreen-logica is via defineExpose aan te roepen en rendert in de DOM.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('@/composables/cytoscape', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    elements: () => ({ remove: vi.fn(), unselect: vi.fn() }),
    getElementById: () => ({ length: 0, select: vi.fn() }),
    animate: vi.fn(), zoom: () => 1, pan: () => ({ x: 0, y: 0 }),
    add: vi.fn(), layout: () => ({ run: vi.fn() }), resize: vi.fn(), fit: vi.fn(), destroy: vi.fn(),
  })),
}))
vi.mock('@/api', () => ({
  api: {
    landschapskaart: { haalGrafdata: vi.fn() },
    applicaties: { haal: vi.fn() },
    componenten: { haal: vi.fn() },
    contracten: { haal: vi.fn() },
    partijen: { haal: vi.fn() },
    relaties: { lijst: vi.fn() },
  },
}))

import { api } from '@/api'
import LandschapskaartView from '@modules/bwb_ontvlechting/frontend/views/LandschapskaartView.vue'

const GRAF = () => ({
  nodes: [
    { id: 'a1', naam: 'Zaaksysteem', element_type: 'applicatie', laag: 'application', lifecycle_status: 'migratieklaar', domein: 'applicatie', hosting_model: 'saas', leverancier_naam: 'SaaS BV', blokkades_open: 0 },
    { id: 'a2', naam: 'Documentbeheer', element_type: 'applicatie', laag: 'application', lifecycle_status: 'geblokkeerd', domein: 'applicatie', hosting_model: 'on_premise', leverancier_naam: null, blokkades_open: 1 },
    { id: 'p1', naam: 'Gemeente X', element_type: 'partij', laag: 'business', soort: 'organisatie', blokkades_open: 0 },
    { id: 'k1', naam: 'Contract X', element_type: 'contract', laag: 'business', blokkades_open: 0 },
    { id: 'db1', naam: 'Oracle DB', element_type: 'database', laag: 'technology', lifecycle_status: 'concept', blokkades_open: 0 },
  ],
  edges: [{ bron_id: 'a1', doel_id: 'a2', relatietype: 'flow', label: 'koppeling', ring: 'applicaties', richting: 'eenrichting', protocol: 'api' }],
})

let wrappers = []
async function mountView() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div/>' } },
      { path: '/landschapskaart', name: 'landschapskaart', component: { template: '<div/>' } },
      { path: '/applicaties/:id', name: 'applicatie-detail', component: { template: '<div/>' } },
    ],
  })
  await router.push('/landschapskaart')
  await router.isReady()
  const pushSpy = vi.spyOn(router, 'push')
  const w = mount(LandschapskaartView, { global: { plugins: [router] } })
  wrappers.push(w)
  await flushPromises()
  return { w, pushSpy }
}

beforeEach(() => {
  vi.clearAllMocks()
  api.landschapskaart.haalGrafdata.mockResolvedValue(GRAF())
})
afterEach(() => {
  wrappers.forEach((w) => w.unmount())
  wrappers = []
  vi.useRealTimers()
  vi.restoreAllMocks()
})

const veld = (w, label) => {
  const dts = w.findAll('[data-testid="lk-popup-velden"] dt')
  const dt = dts.find((d) => d.text() === label)
  return dt ? dt.element.nextElementSibling.textContent : null
}

describe('Landschapskaart — koppeling-popup', () => {
  it('toont Uitgaand + tegenpartij + protocol/datastroom/impact/omschrijving', async () => {
    api.relaties.lijst.mockResolvedValue({ items: [{ id: 'r1', kenmerken: { protocol: 'api', richting: 'eenrichting', impact_bij_verbreking: 'hoog' }, omschrijving: 'Zaak naar DMS' }] })
    const { w } = await mountView()
    // ego-center = a1 (eerste applicatie) → a1→a2 is UITGAAND.
    await w.vm.openEdgePopup({ bron_id: 'a1', doel_id: 'a2', ring: 'applicaties', richting: 'eenrichting', protocol: 'api' })
    await flushPromises()
    expect(w.find('[data-testid="lk-popup"]').exists()).toBe(true)
    expect(w.find('[data-testid="lk-popup-badge"]').text()).toBe('Uitgaand')
    expect(veld(w, 'Tegenpartij')).toBe('Documentbeheer')
    expect(veld(w, 'Type')).toBe('koppeling')
    expect(veld(w, 'Protocol')).toBeTruthy()
    expect(veld(w, 'Datastroom')).toBeTruthy()   // richting-kenmerk, NIET inkomend/uitgaand
    expect(veld(w, 'Impact bij verbreking')).toBeTruthy()
    expect(veld(w, 'Omschrijving')).toBe('Zaak naar DMS')
  })

  it('inkomend/uitgaand wordt afgeleid t.o.v. de ego-node (doel == ego → Inkomend)', async () => {
    api.relaties.lijst.mockResolvedValue({ items: [{ kenmerken: {}, omschrijving: null }] })
    const { w } = await mountView()
    // edge a2→a1 met ego=a1 → doel == ego → INKOMEND.
    await w.vm.openEdgePopup({ bron_id: 'a2', doel_id: 'a1', ring: 'applicaties' })
    await flushPromises()
    expect(w.find('[data-testid="lk-popup-badge"]').text()).toBe('Inkomend')
    expect(veld(w, 'Tegenpartij')).toBe('Documentbeheer')
  })

  it('403 op de relatie-fetch toont een nette melding (geen technische fout)', async () => {
    api.relaties.lijst.mockRejectedValue({ status: 403 })
    const { w } = await mountView()
    await w.vm.openEdgePopup({ bron_id: 'a1', doel_id: 'a2', ring: 'applicaties', protocol: 'api', richting: 'eenrichting' })
    await flushPromises()
    expect(w.find('[data-testid="lk-popup-melding"]').exists()).toBe(true)
    expect(veld(w, 'Protocol')).toBeTruthy() // pre-fill uit de edge blijft staan
  })
})

describe('Landschapskaart — knoop-popup (dispatch per soort)', () => {
  it('applicatie → /applicaties met kern-velden', async () => {
    api.applicaties.haal.mockResolvedValue({ id: 'a1', naam: 'Zaaksysteem', lifecycle_status: 'migratieklaar', eigenaar_organisatie_naam: 'ICT', hostingmodel: 'saas', migratiepad: 'rehost', complexiteit: 'hoog', prioriteit: 'midden', beschrijving: 'Kernsysteem' })
    const { w } = await mountView()
    await w.vm.openNodePopup('a1')
    await flushPromises()
    expect(api.applicaties.haal).toHaveBeenCalledWith('a1')
    expect(w.find('[data-testid="lk-popup-titel"]').text()).toBe('Zaaksysteem')
    expect(veld(w, 'Eigenaar-organisatie')).toBe('ICT')
    expect(veld(w, 'Migratiepad')).toBeTruthy()
    expect(veld(w, 'Beschrijving')).toBe('Kernsysteem')
    expect(w.find('[data-testid="lk-popup-actie"]').exists()).toBe(true) // Open applicatie →
  })

  it('contract → /contracten met looptijd + leverancier', async () => {
    api.contracten.haal.mockResolvedValue({ id: 'k1', contractnaam: 'Contract X', leverancier_naam: 'Acme', contracttype: 'raamcontract', begindatum: '2025-01-01', einddatum: '2027-12-31', omschrijving: 'DMS-licentie' })
    const { w } = await mountView()
    await w.vm.openNodePopup('k1')
    await flushPromises()
    expect(api.contracten.haal).toHaveBeenCalledWith('k1')
    expect(veld(w, 'Leverancier')).toBe('Acme')
    expect(veld(w, 'Looptijd')).toContain('2025-01-01')
    expect(veld(w, 'Omschrijving')).toBe('DMS-licentie')
  })

  it('partij → /partijen met alleen ingevulde contactvelden', async () => {
    api.partijen.haal.mockResolvedValue({ id: 'p1', naam: 'Gemeente X', aard: 'organisatie', plaats: 'Tiel', email: 'info@x.nl', telefoon: null, mobiel: null })
    const { w } = await mountView()
    await w.vm.openNodePopup('p1')
    await flushPromises()
    expect(api.partijen.haal).toHaveBeenCalledWith('p1')
    expect(veld(w, 'E-mail')).toBe('info@x.nl')
    expect(veld(w, 'Adres')).toBe('Tiel')
    expect(veld(w, 'Telefoon')).toBeNull() // leeg → geen regel
  })

  it('infra-component (database) → /componenten', async () => {
    api.componenten.haal.mockResolvedValue({ id: 'db1', naam: 'Oracle DB', componenttype_label: 'Database', lifecycle_status: 'concept', hostingmodel: 'on_premise', beschrijving: null })
    const { w } = await mountView()
    await w.vm.openNodePopup('db1')
    await flushPromises()
    expect(api.componenten.haal).toHaveBeenCalledWith('db1')
    expect(veld(w, 'Type')).toBe('Database')
    expect(w.find('[data-testid="lk-popup-actie"]').exists()).toBe(false) // geen applicatie-doorklik
  })

  it('pre-fill toont meteen node-data terwijl de fetch nog loopt; 403 valt netjes terug', async () => {
    let los
    api.applicaties.haal.mockReturnValue(new Promise((res) => { los = res }))
    const { w } = await mountView()
    w.vm.openNodePopup('a1') // niet awaiten: de fetch blijft hangen tot los()
    await flushPromises()
    // pre-fill zichtbaar vóór resolve (titel + node-velden)
    expect(w.find('[data-testid="lk-popup-titel"]').text()).toBe('Zaaksysteem')
    expect(w.find('[data-testid="lk-popup-laden"]').exists()).toBe(true)
    los({ id: 'a1', naam: 'Zaaksysteem', lifecycle_status: 'migratieklaar' })
    await flushPromises()
    expect(w.find('[data-testid="lk-popup-laden"]').exists()).toBe(false)
  })
})

describe('Landschapskaart — enkele vs. dubbele klik', () => {
  it('enkele klik opent (na drempel) de popup; dubbelklik hercentreert en opent GEEN popup', async () => {
    vi.useFakeTimers()
    api.applicaties.haal.mockResolvedValue({ id: 'a1', naam: 'Zaaksysteem', lifecycle_status: 'migratieklaar' })
    const { w } = await mountView()

    // Dubbelklik: twee taps binnen de drempel → geen popup.
    w.vm.onNodeTap('a1')
    w.vm.onNodeTap('a1')
    vi.advanceTimersByTime(300)
    await flushPromises()
    expect(w.vm.popupOpen).toBe(false)

    // Enkele klik: één tap, drempel verstrijkt → popup opent.
    w.vm.onNodeTap('a1')
    vi.advanceTimersByTime(300)
    await flushPromises()
    expect(w.vm.popupOpen).toBe(true)
  })
})

describe('Landschapskaart — fullscreen-overlay', () => {
  it('toggelt fullscreen-classes en behoudt een open popup; Escape sluit', async () => {
    api.applicaties.haal.mockResolvedValue({ id: 'a1', naam: 'Zaaksysteem' })
    const { w } = await mountView()
    await w.vm.openNodePopup('a1')
    await flushPromises()

    expect(w.find('[data-testid="lk-fullscreen-open"]').exists()).toBe(true)
    w.vm.toggleFullscreen()
    await flushPromises()
    expect(w.vm.fullscreen).toBe(true)
    expect(w.find('[data-testid="lk-wrapper"]').classes()).toContain('fixed')
    expect(w.find('[data-testid="lk-fullscreen-sluit"]').exists()).toBe(true)
    // staat-behoud: popup blijft open na de toggle.
    expect(w.find('[data-testid="lk-popup"]').exists()).toBe(true)

    // Escape sluit eerst de popup (niet de fullscreen).
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await flushPromises()
    expect(w.vm.popupOpen).toBe(false)
    expect(w.vm.fullscreen).toBe(true)
    // tweede Escape sluit de fullscreen.
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await flushPromises()
    expect(w.vm.fullscreen).toBe(false)
  })
})
