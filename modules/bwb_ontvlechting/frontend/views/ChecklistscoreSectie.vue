<script setup>
/**
 * ChecklistscoreSectie — inline scoringslijst over de 89 ChecklistVragen.
 *
 * Join client-side op CODE: ChecklistVraag.code ↔ Checklistscore.vraag_code
 * (het datamodel kent geen vraag_id). Per vraag een ja/deels/nee/nvt-keuze die
 * direct opslaat: nog niet gescoord → maak({applicatie_id, vraag_code, score});
 * al gescoord → werkBij(scoreId, {score}). Per-rij inline feedback i.p.v. 89
 * toasts. Elke geslaagde score kan een blokkade laten ontstaan/oplossen en de
 * lifecycle herberekenen (backend) → de sectie emit 'gewijzigd' zodat de ouder
 * de lifecycle-indicator én de blokkadelijst herlaadt.
 */
import { computed, reactive, ref } from 'vue'
import { useToast } from '@/primevue'
import { useAuthStore } from '@/store/auth'
import { api } from '@/api'
import { SCORE, label } from '../labels'

const props = defineProps({ applicatieId: { type: String, required: true } })
const emit = defineEmits(['gewijzigd'])
const auth = useAuthStore()
const toast = useToast()

const mag = computed(() => auth.hasRole('medewerker', 'beheerder'))

const vragen = ref([])
const scoreMap = reactive({}) // vraag_code -> { id, score }
const opties = ref({ score: [] })
const laden = ref(false)
const fout = ref(null)
const rijStatus = reactive({}) // vraag_code -> 'bezig' | 'opgeslagen' | 'fout'
const rijFout = reactive({}) // vraag_code -> melding

const aantalVragen = computed(() => vragen.value.length)
const aantalGescoord = computed(() => Object.keys(scoreMap).length)

function _toastFout(e) {
  const per = { 403: 'Geen rechten voor deze actie.', 404: 'Niet gevonden.', 409: 'Conflict.' }
  toast.add({ severity: 'error', summary: 'Fout', detail: per[e?.status] || e?.message || 'Er ging iets mis.', life: 5000 })
}

function _vulScoreMap(scores) {
  for (const k of Object.keys(scoreMap)) delete scoreMap[k]
  for (const s of scores) scoreMap[s.vraag_code] = { id: s.id, score: s.score }
}

async function _laadScores() {
  const p = await api.checklistscores.lijst({ applicatieId: props.applicatieId, limit: 100 })
  _vulScoreMap(p.items)
}

async function laad() {
  laden.value = true
  fout.value = null
  try {
    const [vragenResp] = await Promise.all([
      api.checklistvragen.lijst(),
      _laadScores(),
      (async () => {
        if (!opties.value.score.length) opties.value = await api.checklistscores.opties()
      })(),
    ])
    vragen.value = vragenResp
  } catch (e) {
    fout.value = e?.message || 'Laden van de checklist mislukt.'
  } finally {
    laden.value = false
  }
}

function huidigeScore(code) {
  return scoreMap[code]?.score ?? ''
}

async function onScoreChange(code, nieuweScore) {
  if (!nieuweScore) return
  rijStatus[code] = 'bezig'
  delete rijFout[code]
  try {
    const bestaand = scoreMap[code]
    if (bestaand) {
      const r = await api.checklistscores.werkBij(bestaand.id, { score: nieuweScore })
      scoreMap[code] = { id: r.id, score: r.score }
    } else {
      try {
        const r = await api.checklistscores.maak({
          applicatie_id: props.applicatieId,
          vraag_code: code,
          score: nieuweScore,
        })
        scoreMap[code] = { id: r.id, score: r.score }
      } catch (e) {
        if (e?.status === 409) {
          // race: score bestaat al → ophalen en bijwerken
          await _laadScores()
          const id = scoreMap[code]?.id
          const r = await api.checklistscores.werkBij(id, { score: nieuweScore })
          scoreMap[code] = { id: r.id, score: r.score }
        } else {
          throw e
        }
      }
    }
    rijStatus[code] = 'opgeslagen'
    emit('gewijzigd')
  } catch (e) {
    rijStatus[code] = 'fout'
    if (e?.status === 422 && Array.isArray(e.detail)) {
      rijFout[code] = e.detail[0]?.msg || 'Ongeldige waarde.'
    } else {
      _toastFout(e)
    }
  }
}

defineExpose({ aantalVragen, aantalGescoord, herlaad: () => laad() })

laad()
</script>

<template>
  <section class="card" aria-labelledby="sectie-checklist">
    <div class="flex items-center gap-[var(--cd-space-md)] mb-[var(--cd-space-sm)]">
      <h2 id="sectie-checklist" class="text-[length:var(--cd-text-lg)] font-semibold">Checklist</h2>
      <span data-testid="cs-voortgang" class="ml-auto text-[var(--cd-color-text-muted)] text-[length:var(--cd-text-sm)]">
        {{ aantalGescoord }}/{{ aantalVragen }} gescoord
      </span>
    </div>

    <p v-if="fout" role="alert" data-testid="cs-fout" class="text-[var(--cd-color-danger)] mb-[var(--cd-space-sm)]">{{ fout }}</p>

    <table>
      <thead>
        <tr><th>Code</th><th>Vraag</th><th>Score</th><th></th></tr>
      </thead>
      <tbody>
        <tr v-for="v in vragen" :key="v.code" :data-testid="`cs-rij-${v.code}`">
          <td>{{ v.code }}</td>
          <td>{{ v.vraag }}</td>
          <td>
            <select
              :id="`cs-score-${v.code}`"
              :value="huidigeScore(v.code)"
              :disabled="!mag"
              :aria-label="`Score voor vraag ${v.code}`"
              :aria-invalid="!!rijFout[v.code]"
              :data-testid="`cs-score-${v.code}`"
              class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-[var(--cd-space-xs)] bg-white disabled:opacity-60"
              @change="onScoreChange(v.code, $event.target.value)"
            >
              <option value="" disabled>— niet gescoord —</option>
              <option v-for="s in opties.score" :key="s" :value="s">{{ label(SCORE, s) }}</option>
            </select>
          </td>
          <td>
            <span v-if="rijStatus[v.code] === 'bezig'" :data-testid="`cs-status-${v.code}`" class="text-[var(--cd-color-text-muted)] text-[length:var(--cd-text-xs)]">bezig…</span>
            <span v-else-if="rijStatus[v.code] === 'opgeslagen'" :data-testid="`cs-status-${v.code}`" class="text-[var(--cd-color-success)] text-[length:var(--cd-text-xs)]">opgeslagen</span>
            <span v-else-if="rijFout[v.code]" role="alert" :data-testid="`cs-fout-${v.code}`" class="text-[var(--cd-color-danger)] text-[length:var(--cd-text-xs)]">{{ rijFout[v.code] }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
