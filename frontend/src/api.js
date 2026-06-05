// API-client — fetch met httpOnly cookie (credentials: include).
// Foutformaat conform CLAUDE.md: { fout: { code, http_status, bericht } }.
const BASE = '/api/v1'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (res.status === 401) {
    // sessie verlopen — laat de caller dit afhandelen
    throw new Error('NIET_GEAUTHENTICEERD')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.fout?.bericht || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  me: () => request('/auth/me'),
  logout: () => request('/auth/logout', { method: 'POST' }),
}
