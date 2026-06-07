/** Tests — GebruikersgroepSectie (child-sectie via @modules). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: {
    gebruikersgroepen: {
      lijst: vi.fn(),
      maak: vi.fn(),
      werkBij: vi.fn(),
      verwijder: vi.fn(),
    },
  },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import GebruikersgroepSectie from '@modules/bwb_ontvlechting/frontend/views/GebruikersgroepSectie.vue'

const APP = 'app-1'

async function mountSectie({ rollen = ['beheerder'] } = {}) {
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const wrapper = mount(GebruikersgroepSectie, {
    props: { applicatieId: APP },
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService], stubs: { teleport: true } },
  })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
  api.gebruikersgroepen.lijst.mockResolvedValue({ items: [], volgende_cursor: null })
})
afterEach(() => vi.restoreAllMocks())

describe('GebruikersgroepSectie', () => {
  it('rendert de geladen gebruikersgroepen', async () => {
    api.gebruikersgroepen.lijst.mockResolvedValueOnce({
      items: [{ id: 'g1', organisatie: 'Gemeente Tiel', afdeling: 'Burgerzaken', aantal_gebruikers: 12 }],
      volgende_cursor: null,
    })
    const w = await mountSectie()
    expect(api.gebruikersgroepen.lijst).toHaveBeenCalledWith({ applicatieId: APP, limit: 25, after: undefined })
    expect(w.text()).toContain('Gemeente Tiel')
  })

  it('rol-gating: viewer geen Toevoegen, medewerker wel', async () => {
    expect((await mountSectie({ rollen: ['viewer'] })).find('[data-testid="gg-toevoegen"]').exists()).toBe(false)
    expect((await mountSectie({ rollen: ['medewerker'] })).find('[data-testid="gg-toevoegen"]').exists()).toBe(true)
  })

  it('validatie blokkeert submit bij lege organisatie', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="gg-toevoegen"]').trigger('click')
    await flushPromises()
    await w.find('[data-testid="gg-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="gg-fout-organisatie"]').exists()).toBe(true)
    expect(api.gebruikersgroepen.maak).not.toHaveBeenCalled()
  })

  it('weigert een negatief aantal gebruikers client-side', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="gg-toevoegen"]').trigger('click')
    await flushPromises()
    await w.find('[data-testid="gg-veld-organisatie"]').setValue('Gemeente Tiel')
    await w.find('[data-testid="gg-veld-aantal"]').setValue('-3')
    await w.find('[data-testid="gg-form"]').trigger('submit')
    await flushPromises()
    expect(w.find('[data-testid="gg-fout-aantal"]').exists()).toBe(true)
    expect(api.gebruikersgroepen.maak).not.toHaveBeenCalled()
  })

  it('focust het eerste veld bij openen', async () => {
    const w = await mountSectie()
    await w.find('[data-testid="gg-toevoegen"]').trigger('click')
    await flushPromises()
    await new Promise((r) => setTimeout(r, 0))
    expect(document.activeElement).toBe(w.find('[data-testid="gg-veld-organisatie"]').element)
  })

  it('maakt aan en ververst de lijst', async () => {
    api.gebruikersgroepen.maak.mockResolvedValueOnce({ id: 'new' })
    const w = await mountSectie()
    const voor = api.gebruikersgroepen.lijst.mock.calls.length
    await w.find('[data-testid="gg-toevoegen"]').trigger('click')
    await flushPromises()
    await w.find('[data-testid="gg-veld-organisatie"]').setValue('Gemeente Tiel')
    await w.find('[data-testid="gg-form"]').trigger('submit')
    await flushPromises()
    expect(api.gebruikersgroepen.maak).toHaveBeenCalledWith({
      organisatie: 'Gemeente Tiel',
      afdeling: null,
      aantal_gebruikers: null,
      applicatie_id: APP,
    })
    expect(api.gebruikersgroepen.lijst.mock.calls.length).toBe(voor + 1)
  })
})
