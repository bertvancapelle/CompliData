<script setup>
/**
 * PlaatsingSignalenView — consistentie-signalering technische plaatsing
 * (ADR-023 Fase F / F-3 stap 2).
 *
 * Read-only attentielijst: per component een zacht signaal waar het checklist-antwoord
 * over technische plaatsing níét overeenkomt met het bestaan van een draait_op-relatie.
 * Geen fout, blokkeert niets. Leunt volledig op `GET /signalen/plaatsing` (server-side
 * afgeleid uit de betekenis-markering × draait_op). Generiek over componenttypen.
 */
import { onMounted, ref } from 'vue'
import { api } from '@/api'
import { humaniseer } from '@modules/bwb_ontvlechting/frontend/labels'

// Leesbare signaalteksten (geen jargon).
const SIGNAAL_LABEL = {
  beoordeeld_niet_vastgelegd: 'Plaatsing beoordeeld maar niet vastgelegd',
  vastgelegd_niet_beoordeeld: 'Plaatsing vastgelegd maar niet beoordeeld',
}

const items = ref([])
const laden = ref(false)
const fout = ref(null)
const eersteGeladen = ref(false)

const signaalLabel = (s) => SIGNAAL_LABEL[s] || s
const typeLabel = (t) => humaniseer(t)

async function laad() {
  laden.value = true
  fout.value = null
  try {
    items.value = await api.signalen.plaatsing()
  } catch (e) {
    fout.value = e?.message || 'Er ging iets mis bij het laden van de plaatsingssignalen.'
  } finally {
    laden.value = false
    eersteGeladen.value = true
  }
}

onMounted(laad)
</script>

<template>
  <section aria-labelledby="signalen-titel">
    <h1
      id="signalen-titel"
      class="mb-[var(--cd-space-sm)] text-[length:var(--cd-text-2xl)] font-semibold text-[var(--cd-color-primary)]"
    >
      Plaatsingssignalen
    </h1>
    <p class="mb-[var(--cd-space-md)] text-[length:var(--cd-text-sm)] text-[var(--cd-color-text-muted)]">
      Attentiepunten waar het antwoord over technische plaatsing niet overeenkomt met of het
      component daadwerkelijk ergens op draait. Een zacht signaal — geen fout, blokkeert niets.
    </p>

    <p v-if="fout" role="alert" data-testid="signalen-fout" class="mb-[var(--cd-space-md)] rounded-[var(--cd-radius-badge)] border border-[var(--cd-color-danger)] bg-[var(--cd-color-danger)]/10 px-[var(--cd-space-md)] py-[var(--cd-space-sm)] text-[var(--cd-color-danger)]">
      {{ fout }}
    </p>
    <p v-if="laden && !eersteGeladen" data-testid="signalen-laden" class="text-[var(--cd-color-text-muted)]">Laden…</p>

    <p
      v-if="eersteGeladen && !laden && items.length === 0"
      data-testid="signalen-leeg"
      class="rounded-[var(--cd-radius-card)] bg-[var(--cd-color-surface)] px-[var(--cd-space-md)] py-[var(--cd-space-md)] text-[var(--cd-color-text-muted)] shadow-[var(--cd-shadow-sm)]"
    >
      Geen plaatsingssignalen — alle beoordeelde plaatsingen komen overeen met de vastgelegde relaties.
    </p>

    <table
      v-else-if="items.length"
      data-testid="signalen-tabel"
      class="w-full bg-[var(--cd-color-surface)] rounded-[var(--cd-radius-card)] shadow-[var(--cd-shadow-sm)] text-[length:var(--cd-text-sm)]"
    >
      <thead>
        <tr class="text-left text-[length:var(--cd-text-xs)] uppercase tracking-wide text-[var(--cd-color-text-muted)]">
          <th class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)]">Component</th>
          <th class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)]">Type</th>
          <th class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)]">Signaal</th>
          <th class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)]">Reden</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="s in items"
          :key="s.component_id"
          :data-testid="`signaal-${s.component_id}`"
          class="border-t border-[var(--cd-color-border)]"
        >
          <td class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)] font-medium">
            <router-link
              :to="{ name: 'component-detail', params: { id: s.component_id } }"
              :data-testid="`signaal-link-${s.component_id}`"
              class="text-[var(--cd-color-primary)] hover:underline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--cd-color-primary)]"
            >
              {{ s.naam }}
            </router-link>
          </td>
          <td class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)]">{{ typeLabel(s.componenttype) }}</td>
          <td class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)]">
            <span
              :data-testid="`signaal-type-${s.component_id}`"
              class="inline-block rounded-[var(--cd-radius-badge)] bg-[var(--cd-color-warning)]/15 px-[var(--cd-space-sm)] py-[2px] text-[var(--cd-color-warning-text,var(--cd-color-text))]"
            >{{ signaalLabel(s.signaal) }}</span>
          </td>
          <td class="px-[var(--cd-space-md)] py-[var(--cd-space-sm)] text-[var(--cd-color-text-muted)]">{{ s.reden }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
