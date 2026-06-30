<script setup>
/**
 * AppTabs — herbruikbare, toegankelijke tablist (WAI-ARIA tabs, CD022).
 *
 * Rendert ALLEEN de tablist (de `role="tab"`-knoppen); de ouder rendert de
 * bijbehorende `role="tabpanel"`-panelen (met `aria-labelledby` = de tab-id).
 * Gebruikt voor beide niveaus (top + categorie-sub-tabs). Automatische activatie
 * (WAI-ARIA-aanbeveling bij goedkope panelwissels — onze panelen blijven gemount):
 * pijltjes/Home/End verplaatsen focus én selectie; Enter/Space activeren de focus-tab.
 *
 * `--lk-`-tokens, geen `<style>`. id-conventie: `${idPrefix}-tab-${key}` /
 * `${idPrefix}-panel-${key}` (de ouder gebruikt dezelfde voor zijn panelen).
 */
const props = defineProps({
  tabs: { type: Array, required: true }, // [{ key, label }]
  modelValue: { type: [String, Number], default: null },
  ariaLabel: { type: String, required: true },
  orientation: { type: String, default: 'horizontal' }, // 'horizontal' | 'vertical'
  idPrefix: { type: String, required: true },
})
const emit = defineEmits(['update:modelValue'])

function selecteer(key) {
  if (key !== props.modelValue) emit('update:modelValue', key)
}

function opToets(e, i) {
  const verticaal = props.orientation === 'vertical'
  const volgende = verticaal ? 'ArrowDown' : 'ArrowRight'
  const vorige = verticaal ? 'ArrowUp' : 'ArrowLeft'
  let doel = null
  if (e.key === volgende) doel = (i + 1) % props.tabs.length
  else if (e.key === vorige) doel = (i - 1 + props.tabs.length) % props.tabs.length
  else if (e.key === 'Home') doel = 0
  else if (e.key === 'End') doel = props.tabs.length - 1
  else if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    selecteer(props.tabs[i].key)
    return
  } else return
  e.preventDefault()
  const sleutel = props.tabs[doel].key
  selecteer(sleutel) // automatische activatie
  // focus verspringt naar de zojuist geactiveerde tab
  e.currentTarget.parentElement
    ?.querySelector(`[data-testid="${props.idPrefix}-tab-${sleutel}"]`)
    ?.focus?.()
}
</script>

<template>
  <div
    role="tablist"
    :aria-label="ariaLabel"
    :aria-orientation="orientation"
    :class="[
      'flex gap-[var(--lk-space-xs)]',
      orientation === 'vertical' ? 'flex-col' : 'flex-wrap',
    ]"
  >
    <button
      v-for="(t, i) in tabs"
      :id="`${idPrefix}-tab-${t.key}`"
      :key="t.key"
      type="button"
      role="tab"
      :aria-selected="t.key === modelValue"
      :aria-controls="`${idPrefix}-panel-${t.key}`"
      :tabindex="t.key === modelValue ? 0 : -1"
      :data-testid="`${idPrefix}-tab-${t.key}`"
      :class="[
        'inline-flex items-center h-10 rounded-[var(--lk-radius-btn)] px-[var(--lk-space-md)] text-[length:var(--lk-text-sm)] text-left',
        'focus:outline-2 focus:outline-offset-2 focus:outline-[var(--lk-color-primary)]',
        t.key === modelValue
          ? 'border-[0.5px] border-[var(--lk-color-primary)] bg-[var(--lk-color-primary)] font-semibold text-white'
          : 'border-[0.5px] border-[var(--lk-color-border)] bg-white text-[var(--lk-color-text)] hover:bg-[var(--lk-color-primary-50)] hover:text-[var(--lk-color-primary-700)]',
      ]"
      @click="selecteer(t.key)"
      @keydown="opToets($event, i)"
    >
      {{ t.label }}
    </button>
  </div>
</template>
