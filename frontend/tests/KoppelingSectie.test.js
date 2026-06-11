/** Tests — KoppelingSectie (child-sectie via @modules; twee richtingen). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: {
    koppelingen: { lijst: vi.fn(), maak: vi.fn(), werkBij: vi.fn(), verwijder: vi.fn(), opties: vi.fn() },
    applicaties: { lijst: vi.fn(), haal: vi.fn() },
  },
}))

import DataTable from 'primevue/datatable'
import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import KoppelingSectie from '@modules/bwb_ontvlechting/frontend/views/KoppelingSectie.vue'

const APP = 'app-1'
const ANDER = 'app-2'

function _kp(id, bron, doel) {
  return {
    id,
    bron_applicatie_id: bron,
    doel_applicatie_id: doel,
    richting: 'eenrichting',
    protocol: 'api',
    impact_bij_verbreking: 'hoog',
    omschrijving: null,
  }
}

async function mountSectie({ rollen = ['beheerder'] } = {}) {
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const wrapper = mount(KoppelingSectie, {
    props: { applicatieId: APP },
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService], stubs: { teleport: true } },
  })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
  api.koppelingen.lijst.mockResolvedValue({ items: [], volgende_cursor: null })
  api.koppelingen.opties.mockResolvedValue({
    richting: ['eenrichting', 'tweerichting'],
    protocol: ['api', 'overig'],
    impact_bij_verbreking: ['laag', 'midden', 'hoog', 'kritiek'],
  })
  api.applicaties.lijst.mockResolvedValue({
    items: [
      { id: APP, naam: 'Deze App' },
      { id: ANDER, naam: 'Andere App' },
    ],
    volgende_cursor: null,
  })
  api.applicaties.haal.mockResolvedValue({ id: APP, naam: 'Deze App' }) // dezeAppNaam (ZoekSelect-label)
})

// ZoekSelect-interactie (CD049): focus → zoek → klik resultaat.
async function kiesZoek(w, prefix, id) {
  await w.find(`[data-testid="${prefix}-input"]`).trigger('focus')
  await flushPromises()
  await w.find(`[data-testid="${prefix}-optie-${id}"]`).trigger('mousedown')
  await flushPromises()
}
afterEach(() => vi.restoreAllMocks())

describe('KoppelingSectie', () => {
  it('doet twee calls (uitgaand bron + inkomend doel) en toont beide sets', async () => {
    api.koppelingen.lijst.mockImplementation(({ bronApplicatieId }) =>
      Promise.resolve(
        bronApplicatieId === APP
          ? { items: [_kp('k1', APP, ANDER)], volgende_cursor: null } // uitgaand
          : { items: [_kp('k2', ANDER, APP)], volgende_cursor: null }, // inkomend
      ),
    )
    const w = await mountSectie()
    // twee calls: één met bron, één met doel
    const calls = api.koppelingen.lijst.mock.calls.map((c) => c[0])
    expect(calls.some((a) => a.bronApplicatieId === APP)).toBe(true)
    expect(calls.some((a) => a.doelApplicatieId === APP)).toBe(true)
    expect(w.find('[data-testid="kp-tabel-uitgaand"]').exists()).toBe(true)
    expect(w.find('[data-testid="kp-tabel-inkomend"]').exists()).toBe(true)
  })

  it('rol-gating: viewer geen Toevoegen, beheerder wel', async () => {
    expect((await mountSectie({ rollen: ['viewer'] })).find('[data-testid="kp-toevoegen"]').exists()).toBe(false)
    expect((await mountSectie({ rollen: ['beheerder'] })).find('[data-testid="kp-toevoegen"]').exists()).toBe(true)
  })

  it('vult bron met de default-app (ZoekSelect-label) en weigert bron == doel', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="kp-toevoegen"]').trigger('click')
    await flushPromises()
    // bron toont de huidige applicatie als startwaarde
    expect(w.find('[data-testid="kp-veld-bron-input"]').element.value).toBe('Deze App')
    // zet doel == bron (APP) via de zoek-combobox
    await kiesZoek(w, 'kp-veld-doel', APP)
    await w.find('[data-testid="kp-veld-richting"]').setValue('eenrichting')
    await w.find('[data-testid="kp-veld-protocol"]').setValue('api')
    await w.find('[data-testid="kp-veld-impact_bij_verbreking"]').setValue('hoog')
    await w.find('[data-testid="kp-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="kp-fout-doel"]').exists()).toBe(true)
    expect(api.koppelingen.maak).not.toHaveBeenCalled()
  })

  it('maakt aan met geldige bron≠doel en ververst beide richtingen', async () => {
    api.koppelingen.maak.mockResolvedValueOnce({ id: 'new' })
    const w = await mountSectie()
    const voor = api.koppelingen.lijst.mock.calls.length
    await w.find('[data-testid="kp-toevoegen"]').trigger('click')
    await flushPromises()
    await kiesZoek(w, 'kp-veld-doel', ANDER)
    await w.find('[data-testid="kp-veld-richting"]').setValue('eenrichting')
    await w.find('[data-testid="kp-veld-protocol"]').setValue('api')
    await w.find('[data-testid="kp-veld-impact_bij_verbreking"]').setValue('hoog')
    await w.find('[data-testid="kp-form"]').trigger('submit')
    await flushPromises()
    expect(api.koppelingen.maak).toHaveBeenCalledTimes(1)
    expect(api.koppelingen.maak.mock.calls[0][0]).toMatchObject({
      bron_applicatie_id: APP,
      doel_applicatie_id: ANDER,
    })
    // beide richtingen herladen (2 extra calls)
    expect(api.koppelingen.lijst.mock.calls.length).toBe(voor + 2)
  })

  it('per-richting "Meer laden" gebruikt de cursor van de juiste richting', async () => {
    api.koppelingen.lijst.mockImplementation(({ bronApplicatieId }) =>
      Promise.resolve(
        bronApplicatieId === APP
          ? { items: [_kp('k1', APP, ANDER)], volgende_cursor: 'cur-uit' }
          : { items: [_kp('k2', ANDER, APP)], volgende_cursor: null },
      ),
    )
    const w = await mountSectie()
    expect(w.find('[data-testid="kp-meer-uitgaand"]').exists()).toBe(true)
    expect(w.find('[data-testid="kp-meer-inkomend"]').exists()).toBe(false)
    await w.find('[data-testid="kp-meer-uitgaand"]').trigger('click')
    await flushPromises()
    expect(api.koppelingen.lijst).toHaveBeenLastCalledWith({ bronApplicatieId: APP, limit: 25, after: 'cur-uit' })
  })

  it('sorteerklik op de uitgaande tabel → refetch met sort/order + cursor-reset (CD020)', async () => {
    api.koppelingen.lijst.mockResolvedValue({ items: [_kp('k1', APP, ANDER)], volgende_cursor: 'cur-uit' })
    const w = await mountSectie()
    // eerste DataTable = uitgaand; sorteer op de tegenpartij-naam (join-kolom)
    w.findAllComponents(DataTable)[0].vm.$emit('sort', { sortField: 'tegenpartij_naam', sortOrder: 1 })
    await flushPromises()
    expect(api.koppelingen.lijst).toHaveBeenCalledWith({
      bronApplicatieId: APP,
      limit: 25,
      after: undefined, // eigen cursor-reset van de uitgaande richting
      sort: 'tegenpartij_naam',
      order: 'asc',
    })
  })
})
