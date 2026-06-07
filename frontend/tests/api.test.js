/**
 * Tests — api.js foutcontract (ADR-014): 401 status-gebaseerd, 422 native detail.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { api } from '@/api'
import { useAuthStore } from '@/store/auth'

function _resp({ status, body }) {
  return {
    status,
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(body),
  }
}

beforeEach(() => {
  setActivePinia(createPinia())
})
afterEach(() => {
  vi.unstubAllGlobals()
})

describe('api.request — 401 (status-gebaseerd)', () => {
  it('herkent 401 met envelope NIET_GEAUTHENTICEERD (status, niet code)', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve(_resp({ status: 401, body: { fout: { code: 'NIET_GEAUTHENTICEERD', http_status: 401, bericht: 'x' } } })),
    ))
    await expect(api.applicaties.lijst()).rejects.toMatchObject({
      message: 'NIET_GEAUTHENTICEERD',
      status: 401,
      code: 'NIET_GEAUTHENTICEERD',
    })
  })

  it('behandelt 401 met code ID_TOKEN_ONGELDIG identiek (status-gebaseerd)', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve(_resp({ status: 401, body: { fout: { code: 'ID_TOKEN_ONGELDIG', http_status: 401, bericht: 'x' } } })),
    ))
    // Zelfde signaal (message), status 401 — alleen de code verschilt.
    await expect(api.applicaties.haal('id')).rejects.toMatchObject({
      message: 'NIET_GEAUTHENTICEERD',
      status: 401,
      code: 'ID_TOKEN_ONGELDIG',
    })
  })
})

describe('api.request — 422 (bewust native detail)', () => {
  it('behoudt de detail-lijst voor veldmapping (CD003/CD004-formulieren)', async () => {
    const detail = [{ loc: ['body', 'naam'], msg: 'verplicht', type: 'missing' }]
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(_resp({ status: 422, body: { detail } }))))
    await expect(
      api.applicaties.maak({ naam: '' }),
    ).rejects.toMatchObject({ status: 422, detail })
  })
})

describe('store.fetchSession — sessie-verloop op status', () => {
  it('zet user op null bij een 401 (ongeacht body-vorm)', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve(_resp({ status: 401, body: { fout: { code: 'NIET_GEAUTHENTICEERD' } } })),
    ))
    const auth = useAuthStore()
    auth.user = { sub: 's', email: 'a@b.nl', roles: [] }
    await auth.fetchSession()
    expect(auth.user).toBeNull()
    expect(auth.isAuthenticated).toBe(false)
  })

  it('zet user bij een geldige sessie (200)', async () => {
    const user = { sub: 's', tenant_id: 't', email: 'a@b.nl', roles: ['beheerder'] }
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(_resp({ status: 200, body: user }))))
    const auth = useAuthStore()
    await auth.fetchSession()
    expect(auth.user).toEqual(user)
    expect(auth.isAuthenticated).toBe(true)
  })
})
