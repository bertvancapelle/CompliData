/**
 * useTheme — Dynamisch tenant-thema laden (ADR-047 B5).
 *
 * Laadt /themes/{tenantSlug}.css als stylesheet in document.head.
 * Retourneert een Promise die resolvet zodra het thema geladen is,
 * zodat de eerste render pas plaatsvindt na thema-activering (geen FOUT).
 */

let currentThemeLink = null

export function useTheme(tenantSlug) {
  return new Promise((resolve, reject) => {
    // Verwijder eerder geladen tenant-thema (bij tenant-switch)
    if (currentThemeLink) {
      currentThemeLink.remove()
      currentThemeLink = null
    }

    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = `/themes/${tenantSlug}.css`
    link.onload = () => resolve()
    link.onerror = () => reject(new Error(`Thema '${tenantSlug}' kon niet geladen worden`))
    document.head.appendChild(link)
    currentThemeLink = link
  })
}
