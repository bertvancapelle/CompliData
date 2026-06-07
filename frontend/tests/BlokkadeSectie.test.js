/** Tests — BlokkadeSectie (read + PATCH; geen toevoegen/verwijderen). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: { blokkades: { lijst: vi.fn(), werkBij: vi.fn(), opties: vi.fn() } },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import BlokkadeSectie from '@modules/bwb_ontvlechting/frontend/views/BlokkadeSectie.vue'

const APP = 'app-1'

function _blok(id, status = 'open') {
  return { id, status, toelichting: 'iets', eigenaar: 'Team' }
}

async function mountSectie({ rollen = ['beheerder'], items = [_blok('b1')] } = {}) {
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  api.blokkades.lijst.mockResolvedValue({ items, volgende_cursor: null })
  const wrapper = mount(BlokkadeSectie, {
    props: { applicatieId: APP },
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService], stubs: { teleport: true } },
  })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
  api.blokkades.opties.mockResolvedValue({ status: ['open', 'in_behandeling', 'opgelost'] })
  api.blokkades.werkBij.mockResolvedValue({ id: 'b1', status: 'opgelost' })
})
afterEach(() => vi.restoreAllMocks())

describe('BlokkadeSectie', () => {
  it('rendert de blokkades en de open-teller', async () => {
    const w = await mountSectie({ items: [_blok('b1', 'open'), _blok('b2', 'opgelost')] })
    expect(api.blokkades.lijst).toHaveBeenCalledWith({ applicatieId: APP, limit: 25, after: undefined })
    expect(w.find('[data-testid="bk-open-teller"]').text()).toContain('1 open')
  })

  it('biedt GEEN toevoegen/verwijderen-affordance', async () => {
    const w = await mountSectie()
    expect(w.find('[data-testid="bk-toevoegen"]').exists()).toBe(false)
    expect(w.find('[data-testid="bk-verwijder-bevestig"]').exists()).toBe(false)
    expect(w.text()).not.toContain('Verwijderen')
  })

  it('bewerkt een blokkade via PATCH (status/toelichting/eigenaar)', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="bk-bewerk-b1"]').trigger('click')
    await flushPromises()
    // status-dropdown bevat alle drie de waarden
    expect(w.find('[data-testid="bk-veld-status"]').findAll('option').length).toBe(3)
    await w.find('[data-testid="bk-veld-status"]').setValue('opgelost')
    await w.find('[data-testid="bk-veld-eigenaar"]').setValue('Migratieteam')
    await w.find('[data-testid="bk-form"]').trigger('submit')
    await flushPromises()
    expect(api.blokkades.werkBij).toHaveBeenCalledWith('b1', {
      status: 'opgelost',
      toelichting: 'iets',
      eigenaar: 'Migratieteam',
    })
    expect(w.emitted('gewijzigd')).toBeTruthy()
  })

  it('toont 422-veldfout in de Dialog op het juiste veld', async () => {
    const err = new Error('val')
    err.status = 422
    err.detail = [{ loc: ['body', 'eigenaar'], msg: 'te lang' }]
    api.blokkades.werkBij.mockRejectedValueOnce(err)
    const w = await mountSectie()
    await w.find('[data-testid="bk-bewerk-b1"]').trigger('click')
    await flushPromises()
    await w.find('[data-testid="bk-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="bk-fout-eigenaar"]').text()).toContain('te lang')
  })
})
