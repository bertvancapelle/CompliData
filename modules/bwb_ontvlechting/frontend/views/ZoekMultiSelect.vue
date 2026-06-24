<script setup>
/**
 * ZoekMultiSelect — doorzoekbare multi-select bovenop ZoekSelect (LI019 sprint 1b/1b-v2).
 * Elke keuze wordt als chip aan de modelValue-array toegevoegd; het zoekveld blijft open voor
 * de volgende keuze (heropenNaKeuze) en sluit pas bij klik buiten het veld of Escape.
 *
 * modelValue = array van geselecteerde waarden (de `idVeld`-waarde uit de optie-items).
 * Chip-tekst: expliciete `chipLabel(waarde)` indien meegegeven, anders het bij selectie gevangen
 * weergave-label (zodat een id-waarde toch als naam toont). Geen selectie = lege array.
 */
import { computed, ref, watch } from 'vue'
import ZoekSelect from './ZoekSelect.vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  zoekFunctie: { type: Function, required: true },
  weergave: { type: Function, default: (item) => item?.naam ?? '' },
  idVeld: { type: String, default: 'id' },
  // Optioneel: leid de chip-tekst af uit de waarde. Niet gezet → het gevangen selectie-label.
  chipLabel: { type: Function, default: null },
  placeholder: { type: String, default: 'Zoeken…' },
  id: { type: String, default: null },
  testid: { type: String, default: 'zms' },
})
const emit = defineEmits(['update:modelValue'])

// Transiente single-select-binding: ZoekSelect kiest één waarde; wij vangen die op, voegen 'm
// toe aan de set en resetten het veld (→ null) zodat de volgende keuze kan volgen.
const keuze = ref(null)
// value → weergave-label, gevuld bij selectie (voor chips waarvan de waarde een id is).
const gevangenLabels = ref({})

watch(keuze, (v) => {
  if (v == null || v === '') return
  if (!props.modelValue.includes(v)) emit('update:modelValue', [...props.modelValue, v])
  keuze.value = null
})

function onKeuze(item) {
  gevangenLabels.value = { ...gevangenLabels.value, [item[props.idVeld]]: props.weergave(item) }
}

const toonChip = computed(() => (v) =>
  props.chipLabel ? props.chipLabel(v) : (gevangenLabels.value[v] ?? String(v)),
)

function verwijder(v) {
  emit('update:modelValue', props.modelValue.filter((x) => x !== v))
}

function wisAlles() {
  emit('update:modelValue', [])
}
</script>

<template>
  <div class="flex flex-col gap-[var(--cd-space-xs)]">
    <ul v-if="modelValue.length" :data-testid="`${testid}-chips`" class="flex flex-wrap gap-1">
      <li
        v-for="v in modelValue"
        :key="v"
        :data-testid="`${testid}-chip-${v}`"
        class="flex items-center gap-1 rounded bg-[var(--cd-color-accent)] px-[var(--cd-space-xs)] py-0.5 text-[length:var(--cd-text-xs)]"
      >
        {{ toonChip(v) }}
        <button
          type="button"
          :data-testid="`${testid}-chip-verwijder-${v}`"
          aria-label="Verwijder filter"
          class="leading-none text-[var(--cd-color-text-muted)] hover:text-[var(--cd-color-danger)]"
          @click="verwijder(v)"
        >×</button>
      </li>
      <li>
        <button
          type="button"
          :data-testid="`${testid}-wis`"
          class="text-[length:var(--cd-text-xs)] text-[var(--cd-color-text-muted)] hover:text-[var(--cd-color-danger)] hover:underline"
          @click="wisAlles"
        >× Wis</button>
      </li>
    </ul>
    <ZoekSelect
      v-model="keuze"
      :zoek-functie="zoekFunctie"
      :weergave="weergave"
      :id-veld="idVeld"
      :placeholder="placeholder"
      :id="id"
      :testid="testid"
      heropen-na-keuze
      @keuze="onKeuze"
    />
  </div>
</template>
