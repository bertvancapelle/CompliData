/**
 * Laag C — Build-CSS-check (UI-borging interactiestates).
 *
 * WAAROM DEZE CHECK BESTAAT (niet schrappen):
 * Tailwind v4 scant standaard alleen de Vite-root (frontend/). Module-views staan
 * buiten die root (modules/<module>/frontend) en worden alleen meegescand dankzij
 * een `@source`-directive in src/assets/main.css. Verdwijnt die directive (of komt
 * er een nieuwe module zonder eigen @source), dan belanden klassen die ALLEEN in
 * module-views voorkomen STIL niet in de gebouwde CSS — precies de tab-hover-bug.
 * vitest merkt dat niet (het assert klasse-STRINGS, niet de gecompileerde CSS).
 * Deze check bouwt productie-CSS en faalt als een kritische interactie-klasse mist.
 *
 * Draai: `npm run test:css-build` (bedoeld voor CI naast `vitest run`).
 */
import { execSync } from 'node:child_process'
import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const FRONTEND = fileURLToPath(new URL('..', import.meta.url))

// Kritische interactie-klassen (selector-namen, na het strippen van CSS-escapes).
// Minificatie raakt alleen de WAARDE (0.5px -> .5px), niet de klasse-naam.
//
// DE-VERVUILING (cruciaal): dit script staat onder frontend/ en wordt dus door
// Tailwind v4 gescand. Stond een te-matchen class-token hier AANEENGESLOTEN, dan
// zou Tailwind die als class-candidate oppikken en de klasse zelf genereren —
// waardoor de check zijn eigen controle waarmaakt (vals-groen). Daarom bouwen we
// elk token uit fragmenten waarin de sluit-`]` is afgesplitst: een los fragment
// met een ongebalanceerde `[` is GEEN geldige Tailwind-candidate, dus er wordt
// niets geseeded. De runtime-join levert alsnog de volledige selector om op te grep'en.
const j = (...delen) => delen.join('')
const VEREIST = [
  { naam: 'tab-hover-bg',      match: j('hover:bg-[var(--lk-color-primary-50)', ']:hover') },
  { naam: 'tab-hover-text',    match: j('hover:text-[var(--lk-color-primary-700)', ']:hover') },
  { naam: 'tab-omlijning',     match: j('border-[0.5px', ']') },
  { naam: 'secondary-vulling', match: j('bg-[var(--lk-color-primary-50)', ']') },
  { naam: 'primary-vulling',   match: j('bg-[var(--lk-color-primary)', ']') },
  { naam: 'danger-vulling',    match: j('bg-[var(--lk-color-danger)', ']') },
]

console.log('[css-build-check] productie-build draaien…')
execSync('npx vite build', { cwd: FRONTEND, stdio: 'inherit' })

const assetsDir = path.join(FRONTEND, 'dist', 'assets')
const cssFile = readdirSync(assetsDir).find((f) => /^index-.*\.css$/.test(f))
if (!cssFile) {
  console.error('[css-build-check] FAAL: geen dist/assets/index-*.css gevonden.')
  process.exit(1)
}
const ruw = readFileSync(path.join(assetsDir, cssFile), 'utf8')
// Strip CSS-escapes (\: \[ \( \) \] \.) zodat we op de leesbare selector matchen.
const css = ruw.replace(/\\/g, '')

let ontbreekt = 0
for (const { naam, match } of VEREIST) {
  if (css.includes(match)) {
    console.log(`  ✓ ${naam}  (${match})`)
  } else {
    console.error(`  ✗ ${naam}  ONTBREEKT in ${cssFile}  (gezocht: ${match})`)
    ontbreekt++
  }
}

if (ontbreekt > 0) {
  console.error(`\n[css-build-check] FAAL: ${ontbreekt} kritische interactie-klasse(n) niet in de build. ` +
    'Waarschijnlijk ontbreekt een @source-directive in main.css voor een module-frontend.')
  process.exit(1)
}
console.log(`\n[css-build-check] OK — alle ${VEREIST.length} kritische interactie-klassen aanwezig in ${cssFile}.`)
