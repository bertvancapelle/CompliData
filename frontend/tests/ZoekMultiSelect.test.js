/** Tests — ZoekMultiSelect (LI019 sprint 1b): chip-multi-select bovenop ZoekSelect. */
import { describe, it, expect, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ZoekMultiSelect from '@modules/bwb_ontvlechting/frontend/views/ZoekMultiSelect.vue'

const OPTIES = [
  { optie_sleutel: 'applicatie', label: 'Applicatie' },
  { optie_sleutel: 'database', label: 'Database' },
]
const maakZoek = (items = OPTIES) =>
  vi.fn(async ({ zoek } = {}) => {
    const q = (zoek || '').toLowerCase()
    return items.filter((o) => !q || o.label.toLowerCase().includes(q))
  })

async function mountMS(props = {}) {
  const w = mount(ZoekMultiSelect, {
    props: {
      modelValue: [],
      zoekFunctie: maakZoek(),
      weergave: (o) => o.label,
      idVeld: 'optie_sleutel',
      chipLabel: (v) => OPTIES.find((o) => o.optie_sleutel === v)?.label || v,
      testid: 'ms',
      ...props,
    },
  })
  await flushPromises()
  return w
}

async function kies(w, sleutel) {
  await w.find('[data-testid="ms-input"]').trigger('focus')
  await flushPromises()
  await w.find(`[data-testid="ms-optie-${sleutel}"]`).trigger('mousedown')
  await flushPromises()
}

describe('ZoekMultiSelect', () => {
  it('een keuze wordt aan modelValue toegevoegd (emit)', async () => {
    const w = await mountMS()
    await kies(w, 'database')
    const emits = w.emitted('update:modelValue')
    expect(emits).toBeTruthy()
    expect(emits.at(-1)[0]).toEqual(['database'])
  })

  it('een reeds-geselecteerde waarde wordt niet nogmaals toegevoegd', async () => {
    const w = await mountMS({ modelValue: ['database'] })
    await kies(w, 'database')
    // Geen nieuwe modelValue-emit (de waarde zat er al in).
    expect(w.emitted('update:modelValue')).toBeFalsy()
  })

  it('rendert chips voor de selectie en verwijdert er een op klik', async () => {
    const w = await mountMS({ modelValue: ['applicatie', 'database'] })
    expect(w.find('[data-testid="ms-chip-applicatie"]').exists()).toBe(true)
    expect(w.find('[data-testid="ms-chip-database"]').text()).toContain('Database')
    await w.find('[data-testid="ms-chip-verwijder-database"]').trigger('click')
    expect(w.emitted('update:modelValue').at(-1)[0]).toEqual(['applicatie'])
  })

  it('geen selectie = lege array, geen chips', async () => {
    const w = await mountMS()
    expect(w.find('[data-testid="ms-chips"]').exists()).toBe(false)
  })

  it('blijft open na een keuze (snel meerdere kiezen achter elkaar)', async () => {
    const w = await mountMS()
    await kies(w, 'database')
    expect(w.find('[data-testid="ms-input"]').attributes('aria-expanded')).toBe('true')
  })

  it('toont het bij selectie gevangen weergave-label als chip wanneer geen chipLabel is gezet', async () => {
    const w = await mountMS({ chipLabel: undefined })
    await kies(w, 'database')
    await w.setProps({ modelValue: w.emitted('update:modelValue').at(-1)[0] })
    expect(w.find('[data-testid="ms-chip-database"]').text()).toContain('Database')
  })

  it('rendert de vaste optie onderaan en toont bij selectie haar eigen label als chip', async () => {
    const w = await mountMS({ vasteOptie: { optie_sleutel: '__zonder__', label: 'Zonder X' } })
    await w.find('[data-testid="ms-input"]').trigger('focus')
    await flushPromises()
    expect(w.find('[data-testid="ms-optie-__zonder__"]').exists()).toBe(true)
    await w.find('[data-testid="ms-optie-__zonder__"]').trigger('mousedown')
    await flushPromises()
    await w.setProps({ modelValue: w.emitted('update:modelValue').at(-1)[0] })
    expect(w.find('[data-testid="ms-chip-__zonder__"]').text()).toContain('Zonder X')
  })

  it('"× Wis" verschijnt alleen bij ≥1 chip en wist de hele selectie', async () => {
    const leeg = await mountMS()
    expect(leeg.find('[data-testid="ms-wis"]').exists()).toBe(false)
    const w = await mountMS({ modelValue: ['applicatie', 'database'] })
    expect(w.find('[data-testid="ms-wis"]').exists()).toBe(true)
    await w.find('[data-testid="ms-wis"]').trigger('click')
    expect(w.emitted('update:modelValue').at(-1)[0]).toEqual([])
  })
})
