<script setup>
/**
 * SignaleringView — coherent Signalering-scherm (ADR-035, Slice 1).
 *
 * Twee tabs:
 *  - "Registratiegaten" — kritieke component-signalen (zonder eigenaar / zonder verantwoordelijke),
 *    read-only via `GET /signalering/registratiegaten`; doorkliklink naar ComponentDetail.
 *  - "Plaatsing" — de bestaande PlaatsingSignalenView, ongewijzigd ingebed.
 *
 * Read-only en informatief: signalering blokkeert niets en past niets aan.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api'
import { humaniseer } from '@modules/bwb_ontvlechting/frontend/labels'
import PlaatsingSignalenView from '@/views/PlaatsingSignalenView.vue'

const tab = ref('registratiegaten')
const zonderEigenaar = ref([])
const zonderVerantwoordelijke = ref([])
const laden = ref(false)
const fout = ref(null)
const eersteGeladen = ref(false)

const lcLabel = (s) => (s ? humaniseer(s) : '—')
const totaal = computed(() => zonderEigenaar.value.length + zonderVerantwoordelijke.value.length)

async function laadGaten() {
  laden.value = true
  fout.value = null
  try {
    const r = await api.signalering.registratiegaten()
    zonderEigenaar.value = r?.component_zonder_eigenaar || []
    zonderVerantwoordelijke.value = r?.component_zonder_verantwoordelijke || []
  } catch (e) {
    fout.value = e?.message || 'Laden van de registratiegaten mislukt.'
  } finally {
    laden.value = false
    eersteGeladen.value = true
  }
}
onMounted(laadGaten)
</script>

<template>
  <section aria-labelledby="signalering-titel">
    <h1
      id="signalering-titel"
      class="mb-[var(--cd-space-sm)] text-[length:var(--cd-text-2xl)] font-semibold text-[var(--cd-color-primary)]"
    >
      Signalering
    </h1>

    <div role="tablist" aria-label="Signalering" class="mb-[var(--cd-space-md)] flex gap-1 border-b border-[var(--cd-color-border)]">
      <button
        type="button" role="tab" data-testid="sig-tab-registratiegaten"
        :aria-selected="tab === 'registratiegaten'"
        :class="['h-10 rounded-t-[var(--cd-radius-btn)] px-[var(--cd-space-md)] text-[length:var(--cd-text-sm)]', tab === 'registratiegaten' ? 'bg-[var(--cd-color-primary)] font-semibold text-white' : 'hover:bg-[var(--cd-color-accent)]']"
        @click="tab = 'registratiegaten'"
      >Registratiegaten</button>
      <button
        type="button" role="tab" data-testid="sig-tab-plaatsing"
        :aria-selected="tab === 'plaatsing'"
        :class="['h-10 rounded-t-[var(--cd-radius-btn)] px-[var(--cd-space-md)] text-[length:var(--cd-text-sm)]', tab === 'plaatsing' ? 'bg-[var(--cd-color-primary)] font-semibold text-white' : 'hover:bg-[var(--cd-color-accent)]']"
        @click="tab = 'plaatsing'"
      >Plaatsing</button>
    </div>

    <!-- Tab 1 — Registratiegaten -->
    <div v-show="tab === 'registratiegaten'" role="tabpanel" data-testid="sig-panel-registratiegaten">
      <p v-if="fout" role="alert" data-testid="sig-fout" class="mb-[var(--cd-space-md)] rounded-[var(--cd-radius-badge)] border border-[var(--cd-color-danger)] bg-[var(--cd-color-danger)]/10 px-[var(--cd-space-md)] py-[var(--cd-space-sm)] text-[var(--cd-color-danger)]">{{ fout }}</p>
      <p v-if="laden && !eersteGeladen" data-testid="sig-laden" class="text-[var(--cd-color-text-muted)]">Laden…</p>

      <p
        v-if="eersteGeladen && !laden && totaal === 0"
        data-testid="sig-leeg"
        class="rounded-[var(--cd-radius-card)] bg-[var(--cd-color-success)]/10 px-[var(--cd-space-md)] py-[var(--cd-space-md)] text-[var(--cd-color-text)]"
      >Geen openstaande registratiegaten.</p>

      <template v-else-if="eersteGeladen && !laden">
        <div v-if="zonderEigenaar.length" class="mb-[var(--cd-space-lg)]" data-testid="sig-zonder-eigenaar">
          <h2 class="mb-[var(--cd-space-sm)] text-[length:var(--cd-text-base)] font-semibold">🔴 Component zonder eigenaar ({{ zonderEigenaar.length }})</h2>
          <ul class="flex flex-col gap-0.5">
            <li v-for="c in zonderEigenaar" :key="c.id" :data-testid="`sig-eigenaar-${c.id}`" class="flex items-center gap-2 text-[length:var(--cd-text-sm)]">
              <router-link :to="{ name: 'component-detail', params: { id: c.id } }" class="text-[var(--cd-color-primary)] hover:underline">{{ c.naam }}</router-link>
              <span class="text-[var(--cd-color-text-muted)]">· {{ lcLabel(c.lifecycle_status) }}</span>
            </li>
          </ul>
        </div>
        <div v-if="zonderVerantwoordelijke.length" data-testid="sig-zonder-verantwoordelijke">
          <h2 class="mb-[var(--cd-space-sm)] text-[length:var(--cd-text-base)] font-semibold">🔴 Component zonder verantwoordelijke ({{ zonderVerantwoordelijke.length }})</h2>
          <ul class="flex flex-col gap-0.5">
            <li v-for="c in zonderVerantwoordelijke" :key="c.id" :data-testid="`sig-verantwoordelijke-${c.id}`" class="flex items-center gap-2 text-[length:var(--cd-text-sm)]">
              <router-link :to="{ name: 'component-detail', params: { id: c.id } }" class="text-[var(--cd-color-primary)] hover:underline">{{ c.naam }}</router-link>
              <span class="text-[var(--cd-color-text-muted)]">· {{ lcLabel(c.lifecycle_status) }}</span>
            </li>
          </ul>
        </div>
      </template>
    </div>

    <!-- Tab 2 — Plaatsing (bestaande view, ongewijzigd) -->
    <div v-show="tab === 'plaatsing'" role="tabpanel" data-testid="sig-panel-plaatsing">
      <PlaatsingSignalenView />
    </div>
  </section>
</template>
