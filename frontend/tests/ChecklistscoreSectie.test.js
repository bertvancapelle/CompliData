/** Tests — ChecklistscoreSectie (inline scoringslijst, join op vraag_code). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: {
    checklistvragen: { lijst: vi.fn() },
    checklistscores: { lijst: vi.fn(), maak: vi.fn(), werkBij: vi.fn(), opties: vi.fn() },
  },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import ChecklistscoreSectie from '@modules/bwb_ontvlechting/frontend/views/ChecklistscoreSectie.vue'

const APP = 'app-1'
const VRAGEN = [
  { id: 1, code: '1.1', categorie_nr: 1, categorie_naam: 'C', vraag: 'Vraag een', prioriteit: 'hoog' },
  { id: 2, code: '1.2', categorie_nr: 1, categorie_naam: 'C', vraag: 'Vraag twee', prioriteit: 'hoog' },
]

async function mountSectie({ rollen = ['medewerker'], categorieNr = null } = {}) {
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const wrapper = mount(ChecklistscoreSectie, {
    props: { applicatieId: APP, categorieNr },
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService] },
  })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
  api.checklistvragen.lijst.mockResolvedValue(VRAGEN)
  api.checklistscores.lijst.mockResolvedValue({
    items: [{ id: 's1', vraag_code: '1.2', score: 'ja' }],
    volgende_cursor: null,
  })
  api.checklistscores.opties.mockResolvedValue({ score: ['ja', 'deels', 'nee', 'nvt'] })
  api.checklistscores.maak.mockResolvedValue({ id: 's2', score: 'nee' })
  api.checklistscores.werkBij.mockResolvedValue({ id: 's1', score: 'nee' })
})
afterEach(() => vi.restoreAllMocks())

describe('ChecklistscoreSectie', () => {
  it('rendert de vragen en de huidige score (ongescoord = leeg)', async () => {
    const w = await mountSectie()
    expect(w.text()).toContain('Vraag een')
    expect(w.find('[data-testid="cs-score-1.1"]').element.value).toBe('') // ongescoord
    expect(w.find('[data-testid="cs-score-1.2"]').element.value).toBe('ja') // gescoord
  })

  it('toont de voortgang X/N', async () => {
    const w = await mountSectie()
    expect(w.find('[data-testid="cs-voortgang"]').text()).toContain('1/2')
  })

  it('maakt een score aan voor een ongescoorde vraag (vraag_code)', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="cs-score-1.1"]').setValue('nee')
    await flushPromises()
    expect(api.checklistscores.maak).toHaveBeenCalledWith({
      applicatie_id: APP,
      vraag_code: '1.1',
      score: 'nee',
    })
    expect(w.emitted('gewijzigd')).toBeTruthy()
  })

  it('werkt een bestaande score bij via het score-id', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="cs-score-1.2"]').setValue('nee')
    await flushPromises()
    expect(api.checklistscores.werkBij).toHaveBeenCalledWith('s1', { score: 'nee' })
    expect(api.checklistscores.maak).not.toHaveBeenCalled()
  })

  it('valt bij 409 (race) terug op werkBij na refetch', async () => {
    const conflict = new Error('bestaat al')
    conflict.status = 409
    api.checklistscores.maak.mockRejectedValueOnce(conflict)
    // na refetch bestaat de score wél
    api.checklistscores.lijst
      .mockResolvedValueOnce({ items: [{ id: 's1', vraag_code: '1.2', score: 'ja' }], volgende_cursor: null })
      .mockResolvedValueOnce({ items: [{ id: 's9', vraag_code: '1.1', score: 'nee' }], volgende_cursor: null })
    const w = await mountSectie()
    await w.find('[data-testid="cs-score-1.1"]').setValue('nee')
    await flushPromises()
    expect(api.checklistscores.werkBij).toHaveBeenCalledWith('s9', { score: 'nee' })
  })

  it('rol-gating: viewer kan niet scoren (controls disabled)', async () => {
    const w = await mountSectie({ rollen: ['viewer'] })
    expect(w.find('[data-testid="cs-score-1.1"]').attributes('disabled')).toBeDefined()
  })

  // ── CD022: filtering op categorie + globale voortgang ──────────────────────
  it('toont met categorieNr alleen de vragen van die categorie (voortgang blijft globaal)', async () => {
    api.checklistvragen.lijst.mockResolvedValue([
      { id: 1, code: '1.1', categorie_nr: 1, categorie_naam: 'Een', vraag: 'V een', prioriteit: 'hoog' },
      { id: 2, code: '2.1', categorie_nr: 2, categorie_naam: 'Twee', vraag: 'V twee', prioriteit: 'hoog' },
    ])
    api.checklistscores.lijst.mockResolvedValue({ items: [], volgende_cursor: null })
    const w = await mountSectie({ categorieNr: 1 })
    expect(w.find('[data-testid="cs-rij-1.1"]').exists()).toBe(true)
    expect(w.find('[data-testid="cs-rij-2.1"]').exists()).toBe(false) // andere categorie verborgen
    // voortgang telt ALLE vragen (globaal), niet alleen de getoonde categorie
    expect(w.find('[data-testid="cs-voortgang"]').text()).toContain('0/2')
  })
})
