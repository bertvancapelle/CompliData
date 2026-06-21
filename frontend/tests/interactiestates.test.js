/**
 * Laag B — Component-render-state-test (UI-borging interactiestates).
 *
 * Bewaakt de twee centrale componenten die de knop-/tab-interactie-taal dragen:
 *  1. presets/Button.js — elke variant zet de juiste token-klasse + één vaste
 *     hoogte (h-10, GEEN size-variatie/h-8 meer).
 *  2. AppTabs.vue — gekozen vs. niet-gekozen tab dragen de juiste token-/state-
 *     klassen, en de hover-klassen staan op het klikbare element (de tab-button).
 *
 * Vangt "state op verkeerd element" en "verkeerde/ontbrekende token-klasse".
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import buttonPreset from '@/presets/Button.js'
import AppTabs from '@modules/bwb_ontvlechting/frontend/views/AppTabs.vue'

// DE-VERVUILING: dit testbestand staat onder frontend/ en wordt door Tailwind v4
// gescand. Module-UNIEKE class-tokens (die alléén in AppTabs voorkomen) mogen hier
// niet AANEENGESLOTEN als literal staan — anders pikt Tailwind ze als candidate op
// en genereert ze zelf, waardoor de build-CSS-check (laag C) vals-groen wordt. We
// bouwen zulke verwachte tokens uit fragmenten (sluit-`]` afgesplitst → ongebalanceerde
// `[` = geen candidate). De assertie vergelijkt alsnog de volledige string.
const cls = (...delen) => delen.join('')

/** Vlakke class-string uit de (array-)class van de preset-root. */
function rootClass(props) {
  const out = buttonPreset.root({ props })
  return [out.class].flat(Infinity).join(' ')
}

describe('Laag B — Button-preset varianten', () => {
  it('primary (default): donkerblauwe vulling + witte tekst', () => {
    const c = rootClass({})
    expect(c).toContain('bg-[var(--cd-color-primary)]')
    expect(c).toContain('text-white')
  })

  it('secondary: lichtblauwe vulling + mid-blauwe tekst (token-klassen)', () => {
    const c = rootClass({ severity: 'secondary' })
    expect(c).toContain('bg-[var(--cd-color-primary-50)]')
    expect(c).toContain('text-[var(--cd-color-primary-700)]')
  })

  it('danger: rode vulling via --cd-color-danger', () => {
    expect(rootClass({ severity: 'danger' })).toContain('bg-[var(--cd-color-danger)]')
  })

  it('text (ghost): transparant + primary-tekst, wint van severity', () => {
    const c = rootClass({ text: true, severity: 'secondary' })
    expect(c).toContain('bg-transparent')
    expect(c).toContain('text-[var(--cd-color-primary)]')
    // ghost wint: geen secondary-vulling
    expect(c).not.toContain('bg-[var(--cd-color-primary-50)]')
  })

  it('één vaste hoogte h-10 op élke variant; geen h-8/size-variatie', () => {
    for (const props of [{}, { severity: 'secondary' }, { severity: 'danger' }, { text: true }, { size: 'small' }]) {
      const c = rootClass(props)
      expect(c, `h-10 ontbreekt voor ${JSON.stringify(props)}`).toContain('h-10')
      expect(c, `h-8 mag niet voorkomen voor ${JSON.stringify(props)}`).not.toContain('h-8')
    }
  })
})

describe('Laag B — AppTabs render-states', () => {
  const tabs = [
    { key: 'a', label: 'Tab A' },
    { key: 'b', label: 'Tab B' },
  ]

  function tabClass(testid) {
    const w = mount(AppTabs, {
      props: { tabs, modelValue: 'a', ariaLabel: 'Test', idPrefix: 't' },
    })
    return w.find(`[data-testid="${testid}"]`)
  }

  it('gekozen tab: donkerblauwe token-vulling + witte tekst', () => {
    const el = tabClass('t-tab-a')
    expect(el.exists()).toBe(true)
    expect(el.classes().join(' ')).toContain('bg-[var(--cd-color-primary)]')
    expect(el.classes().join(' ')).toContain('text-white')
  })

  it('niet-gekozen tab: omlijning + hover-klassen op de tab-button zelf', () => {
    const el = tabClass('t-tab-b')
    const c = el.classes().join(' ')
    // het klikbare element is de tab-button (role=tab), niet een wrapper
    expect(el.attributes('role')).toBe('tab')
    // omlijning (beschikbaar-status) — module-uniek, gede-vervuild
    expect(c).toContain(cls('border-[0.5px', ']'))
    expect(c).toContain('border-[var(--cd-color-border)]')
    // hover-states staan op deze button — module-uniek, gede-vervuild
    expect(c).toContain(cls('hover:bg-[var(--cd-color-primary-50)', ']'))
    expect(c).toContain(cls('hover:text-[var(--cd-color-primary-700)', ']'))
  })
})
