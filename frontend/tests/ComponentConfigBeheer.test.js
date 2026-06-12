/** Tests — ComponentConfigBeheer (platform-beheer componentcatalogus, ADR-021 fase C). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: { platformComponentconfig: { lijst: vi.fn(), maak: vi.fn(), werkBij: vi.fn() } },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import ComponentConfigBeheer from '@/views/ComponentConfigBeheer.vue'

const _opties = () => [
  { id: 1, dimensie: 'componenttype', optie_sleutel: 'applicatie', label: 'Applicatie', volgorde: 0, actief: true },
  { id: 2, dimensie: 'componenttype', optie_sleutel: 'database', label: 'Database', volgorde: 1, actief: true },
  { id: 3, dimensie: 'componenttype', optie_sleutel: 'oud', label: 'Oud', volgorde: 2, actief: false },
  { id: 4, dimensie: 'structuurrelatie_type', optie_sleutel: 'draait_op', label: 'Draait op', volgorde: 0, actief: true },
]

async function mountBeheer({ rollen = ['platformbeheerder'] } = {}) {
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 'p', email: 'b@platform.nl', roles: rollen }
  auth.sessionType = 'platform'
  const w = mount(ComponentConfigBeheer, {
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService], stubs: { teleport: true } },
  })
  await flushPromises()
  return w
}

beforeEach(() => {
  vi.clearAllMocks()
  api.platformComponentconfig.lijst.mockResolvedValue(_opties())
})
afterEach(() => vi.restoreAllMocks())

describe('ComponentConfigBeheer — render', () => {
  it('toont twee dimensies; gedeactiveerde rij onderscheiden', async () => {
    const w = await mountBeheer()
    expect(w.find('[data-testid="cat-sectie-componenttype"]').exists()).toBe(true)
    expect(w.find('[data-testid="cat-sectie-structuurrelatie_type"]').exists()).toBe(true)
    expect(w.text()).toContain('Database')
    expect(w.find('[data-testid="cat-rij-3"]').classes()).toContain('opacity-50')
    expect(w.find('[data-testid="cat-status-3"]').text()).toContain('Gedeactiveerd')
  })

  it('systeem-sleutel applicatie: Systeem-Tag, geen deactiveer-toggle', async () => {
    const w = await mountBeheer()
    expect(w.find('[data-testid="cat-systeem-1"]').exists()).toBe(true)
    expect(w.find('[data-testid="cat-deactiveer-1"]').exists()).toBe(false)
    // bewerken (label/volgorde) blijft wél beschikbaar op de systeem-rij
    expect(w.find('[data-testid="cat-bewerk-1"]').exists()).toBe(true)
    // een gewoon type heeft wél een deactiveer-knop
    expect(w.find('[data-testid="cat-deactiveer-2"]').exists()).toBe(true)
  })

  it('biedt nergens een verwijder-affordance', async () => {
    const w = await mountBeheer()
    expect(w.findAll('[data-testid*="verwijder"]').length).toBe(0)
    expect(w.html()).not.toContain('Verwijderen')
    expect(api.platformComponentconfig.verwijder).toBeUndefined()
  })
})

describe('ComponentConfigBeheer — flows', () => {
  it('toevoegen: sleutel-patroonvalidatie + 409 in-form', async () => {
    const w = await mountBeheer()
    await w.find('[data-testid="cat-toevoegen-componenttype"]').trigger('click')
    await flushPromises()
    await w.find('[data-testid="cat-add-sleutel"]').setValue('ETL Tool')
    await w.find('[data-testid="cat-add-label"]').setValue('ETL-tool')
    await w.find('[data-testid="cat-add-form"]').trigger('submit')
    expect(w.find('[data-testid="cat-add-fout-optie_sleutel"]').exists()).toBe(true)
    expect(api.platformComponentconfig.maak).not.toHaveBeenCalled()

    api.platformComponentconfig.maak.mockRejectedValueOnce({ status: 409, code: 'CONFIGURATIE_CONFLICT', message: 'bestaat al' })
    await w.find('[data-testid="cat-add-sleutel"]').setValue('etl_tool')
    await w.find('[data-testid="cat-add-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="cat-add-formfout"]').exists()).toBe(true)
  })

  it('bewerken: dimensie en sleutel read-only', async () => {
    const w = await mountBeheer()
    await w.find('[data-testid="cat-bewerk-2"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-testid="cat-edit-sleutel-readonly"]').text()).toContain('database')
    expect(w.find('[data-testid="cat-edit-dimensie-readonly"]').text()).toContain('Componenttypen')
    expect(w.find('input[data-testid="cat-edit-sleutel"]').exists()).toBe(false)
  })

  it('deactiveren: bevestiging + werkBij actief=false', async () => {
    api.platformComponentconfig.werkBij.mockResolvedValueOnce({ ..._opties()[1], actief: false })
    const w = await mountBeheer()
    await w.find('[data-testid="cat-deactiveer-2"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-testid="cat-deact-uitleg"]').text()).toContain('blijven leesbaar')
    await w.find('[data-testid="cat-deact-bevestig"]').trigger('click')
    await flushPromises()
    expect(api.platformComponentconfig.werkBij).toHaveBeenCalledWith(2, { actief: false })
  })
})

describe('ComponentConfigBeheer — rol-gating', () => {
  it('platformoperator: alles read-only', async () => {
    const w = await mountBeheer({ rollen: ['platformoperator'] })
    expect(w.find('[data-testid="cat-toevoegen-componenttype"]').exists()).toBe(false)
    expect(w.find('[data-testid="cat-bewerk-2"]').exists()).toBe(false)
    expect(w.find('[data-testid="cat-deactiveer-2"]').exists()).toBe(false)
    expect(w.text()).toContain('Database')  // catalogus zelf wél zichtbaar
  })
})
