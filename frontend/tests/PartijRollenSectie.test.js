/** Tests — PartijRollenSectie (rollen van één partij op objecten; ADR-024 slice 2b + DC013 toevoegen). */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

vi.mock('@/api', () => ({
  api: {
    roltoewijzingen: { lijst: vi.fn(), rollen: vi.fn(), maak: vi.fn() },
    componenten: { lijst: vi.fn() },
    contracten: { lijst: vi.fn() },
  },
}))

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'
import PartijRollenSectie from '@modules/bwb_ontvlechting/frontend/views/PartijRollenSectie.vue'

const PARTIJ = 'p1'

function maakRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/componenten/:id', name: 'component-detail', component: { template: '<div/>' } },
      { path: '/contracten/:id', name: 'contract-detail', component: { template: '<div/>' } },
    ],
  })
}

async function mountSectie({ rollen = ['beheerder'] } = {}) {
  const router = maakRouter()
  await router.push('/componenten/c1')
  await router.isReady()
  const pinia = createPinia()
  const auth = useAuthStore(pinia)
  auth.user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: rollen }
  const w = mount(PartijRollenSectie, {
    props: { partijId: PARTIJ },
    attachTo: document.body,
    global: { plugins: [pinia, [PrimeVue, { unstyled: true }], ToastService, router], stubs: { teleport: true } },
  })
  await flushPromises()
  return w
}

beforeEach(() => {
  vi.clearAllMocks()
  api.roltoewijzingen.lijst.mockResolvedValue([
    { toewijzing_id: 't1', rol: 'eigenaar', rol_label: 'Eigenaar', object_id: 'c1', object_naam: 'Zaaksysteem', object_type: 'component' },
    { toewijzing_id: 't2', rol: 'contractbeheer', rol_label: 'Contractbeheer', object_id: 'k1', object_naam: 'Mantel X', object_type: 'contract' },
  ])
  api.roltoewijzingen.rollen.mockResolvedValue([
    { optie_sleutel: 'eigenaar', label: 'Eigenaar' },
    { optie_sleutel: 'contractbeheer', label: 'Contractbeheer' },
  ])
  api.componenten.lijst.mockResolvedValue({ items: [{ id: 'c9', naam: 'Nieuw component', componenttype_label: 'Database' }], volgende_cursor: null })
  api.contracten.lijst.mockResolvedValue({ items: [{ id: 'k9', contractnaam: 'Nieuw contract' }], volgende_cursor: null })
})
afterEach(() => vi.restoreAllMocks())

describe('PartijRollenSectie', () => {
  it('toont object-naam, type en rol-label per regel', async () => {
    const w = await mountSectie()
    const t = w.find('[data-testid="pr-tabel"]').text()
    expect(t).toContain('Zaaksysteem')
    expect(t).toContain('Eigenaar')
    expect(t).toContain('Mantel X')
    expect(t).toContain('Contractbeheer')
    expect(api.roltoewijzingen.lijst).toHaveBeenCalledWith({ partij_id: PARTIJ })
  })

  it('linkt een component-rij naar component-detail en een contract-rij naar contract-detail', async () => {
    const w = await mountSectie()
    const hrefs = w.findAll('[data-testid="pr-object-link"]').map((a) => a.attributes('href'))
    expect(hrefs.some((h) => h.includes('/componenten/c1'))).toBe(true)
    expect(hrefs.some((h) => h.includes('/contracten/k1'))).toBe(true)
  })

  it('lege staat zonder rollen wijst naar de toevoeg-actie en de objecten', async () => {
    api.roltoewijzingen.lijst.mockResolvedValueOnce([])
    const w = await mountSectie()
    const leeg = w.find('[data-testid="pr-leeg"]')
    expect(leeg.exists()).toBe(true)
    expect(leeg.text()).toContain('Rol toevoegen')
  })

  it('rol-gating: viewer geen toevoeg-knop, beheerder wel', async () => {
    expect((await mountSectie({ rollen: ['viewer'] })).find('[data-testid="pr-toevoegen"]').exists()).toBe(false)
    expect((await mountSectie({ rollen: ['beheerder'] })).find('[data-testid="pr-toevoegen"]').exists()).toBe(true)
  })

  it('DC013: voegt vanuit de partij een rol toe op een gekozen object', async () => {
    api.roltoewijzingen.maak.mockResolvedValueOnce({ toewijzing_id: 'nieuw' })
    const w = await mountSectie()
    await w.find('[data-testid="pr-toevoegen"]').trigger('click')
    await flushPromises()
    // Object kiezen via de zoek-combobox (component + contract gemerged).
    await w.find('[data-testid="pr-veld-object-input"]').trigger('focus')
    await flushPromises()
    expect(api.componenten.lijst).toHaveBeenCalled()
    expect(api.contracten.lijst).toHaveBeenCalled()
    await w.find('[data-testid="pr-veld-object-optie-c9"]').trigger('mousedown')
    await w.find('[data-testid="pr-veld-rol"]').setValue('eigenaar')
    await w.find('[data-testid="pr-form"]').trigger('submit')
    await flushPromises()
    expect(api.roltoewijzingen.maak).toHaveBeenCalledWith({ partij_id: PARTIJ, object_id: 'c9', rol: 'eigenaar' })
  })
})
