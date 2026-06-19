/** Tests — VraagBetekenis- + Partijsoort-ConfigBeheer (platform-beheer, enkel-doel catalogi). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: {
    platformVraagbetekenisconfig: { lijst: vi.fn(), maak: vi.fn(), werkBij: vi.fn() },
    platformPartijsoortconfig: { lijst: vi.fn(), maak: vi.fn(), werkBij: vi.fn() },
  },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import VraagBetekenisConfigBeheer from '@/views/VraagBetekenisConfigBeheer.vue'
import PartijsoortConfigBeheer from '@/views/PartijsoortConfigBeheer.vue'

// (component, api-resource, testid-prefix)
const SCHERMEN = [
  { naam: 'vraagbetekenis', comp: VraagBetekenisConfigBeheer, res: 'platformVraagbetekenisconfig', p: 'vb' },
  { naam: 'partijsoort', comp: PartijsoortConfigBeheer, res: 'platformPartijsoortconfig', p: 'ps' },
]

const _opties = () => [
  { id: 1, optie_sleutel: 'leverancier', label: 'Leverancier', volgorde: 0, actief: true },
  { id: 2, optie_sleutel: 'oud', label: 'Oud', volgorde: 1, actief: false },
]

async function mountBeheer(comp, { rollen = ['platformbeheerder'] } = {}) {
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 'p', email: 'b@platform.nl', roles: rollen }
  auth.sessionType = 'platform'
  const w = mount(comp, {
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService], stubs: { teleport: true } },
  })
  await flushPromises()
  return w
}

beforeEach(() => vi.clearAllMocks())
afterEach(() => vi.restoreAllMocks())

describe.each(SCHERMEN)('$naam-ConfigBeheer', ({ comp, res, p }) => {
  beforeEach(() => api[res].lijst.mockResolvedValue(_opties()))

  it('toont de opties; gedeactiveerde rij onderscheiden', async () => {
    const w = await mountBeheer(comp)
    expect(w.text()).toContain('Leverancier')
    expect(w.find(`[data-testid="${p}-rij-2"]`).classes()).toContain('opacity-50')
    expect(w.find(`[data-testid="${p}-status-2"]`).text()).toContain('Gedeactiveerd')
    expect(w.find(`[data-testid="${p}-reactiveer-2"]`).exists()).toBe(true)
  })

  it('voegt een optie toe via de dialog', async () => {
    api[res].maak.mockResolvedValue({ id: 9, optie_sleutel: 'ketenpartner', label: 'Ketenpartner', volgorde: 2, actief: true })
    const w = await mountBeheer(comp)
    await w.find(`[data-testid="${p}-toevoegen"]`).trigger('click')
    await w.find(`[data-testid="${p}-add-sleutel"]`).setValue('ketenpartner')
    await w.find(`[data-testid="${p}-add-label"]`).setValue('Ketenpartner')
    await w.find(`[data-testid="${p}-add-form"]`).trigger('submit')
    await flushPromises()
    expect(api[res].maak).toHaveBeenCalledWith(expect.objectContaining({ optie_sleutel: 'ketenpartner', label: 'Ketenpartner' }))
  })

  it('weigert een ongeldige sleutel client-side (geen API-call)', async () => {
    const w = await mountBeheer(comp)
    await w.find(`[data-testid="${p}-toevoegen"]`).trigger('click')
    await w.find(`[data-testid="${p}-add-sleutel"]`).setValue('Met Spatie')
    await w.find(`[data-testid="${p}-add-label"]`).setValue('X')
    await w.find(`[data-testid="${p}-add-form"]`).trigger('submit')
    await flushPromises()
    expect(w.find(`[data-testid="${p}-add-fout-optie_sleutel"]`).exists()).toBe(true)
    expect(api[res].maak).not.toHaveBeenCalled()
  })

  it('deactiveert een optie (soft)', async () => {
    api[res].werkBij.mockResolvedValue({ id: 1, optie_sleutel: 'leverancier', label: 'Leverancier', volgorde: 0, actief: false })
    const w = await mountBeheer(comp)
    await w.find(`[data-testid="${p}-deactiveer-1"]`).trigger('click')
    await w.find(`[data-testid="${p}-deact-bevestig"]`).trigger('click')
    await flushPromises()
    expect(api[res].werkBij).toHaveBeenCalledWith(1, { actief: false })
  })

  it('verbergt beheer-acties zonder platformbeheerder-rol', async () => {
    const w = await mountBeheer(comp, { rollen: ['platformoperator'] })
    expect(w.find(`[data-testid="${p}-toevoegen"]`).exists()).toBe(false)
    expect(w.find(`[data-testid="${p}-deactiveer-1"]`).exists()).toBe(false)
    expect(w.find(`[data-testid="${p}-bewerk-1"]`).exists()).toBe(false)
  })
})
