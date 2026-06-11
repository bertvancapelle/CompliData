<script setup>
/**
 * ContractDetail — read-only weergave + acties (ADR-020 contractregister).
 *
 * Toont de geresolveerde dekking-/kostenmodel-labels als Tags (uit de Read-resolutie,
 * incl. inactieve sleutels). Een deelcontract linkt naar zijn mantelcontract.
 * Verwijderen via Dialog; een mantel met deelcontracten of een gekoppeld contract
 * levert 409 `IN_GEBRUIK` → nette Toast. (Overzichten mantel→deel = Fase D2.)
 */
import { computed, onMounted, ref } from 'vue'
import { Button, Dialog, Tag, useToast } from '@/primevue'
import { useRouter } from '@/composables/router'
import { useAuthStore } from '@/store/auth'
import { api } from '@/api'
import { CONTRACTTYPE, CONTRACTTYPE_SEVERITY, REGISTER_FOUT, label } from '../labels'

const props = defineProps({ id: { type: String, required: true } })
const router = useRouter()
const toast = useToast()
const auth = useAuthStore()

const contract = ref(null)
const fout = ref(null)
const bezig = ref(false)
const verwijderDialog = ref(false)

const magBewerken = computed(() => auth.hasRole('medewerker', 'beheerder'))
const magVerwijderen = computed(() => auth.hasRole('beheerder'))

function _toastFout(e) {
  const detail =
    e?.status === 409
      ? e?.message || REGISTER_FOUT[e?.code] || 'Dit contract is nog in gebruik.'
      : { 403: 'Je hebt geen rechten voor deze actie.', 404: 'Het contract is niet (meer) gevonden.' }[e?.status] ||
        e?.message ||
        'Er ging iets mis.'
  toast.add({ severity: 'error', summary: 'Fout', detail, life: 5000 })
}

async function laad() {
  fout.value = null
  try {
    contract.value = await api.contracten.haal(props.id)
  } catch (e) {
    fout.value = e?.status === 404 ? 'Dit contract bestaat niet (meer).' : e?.message || 'Er ging iets mis.'
    _toastFout(e)
  }
}

async function bevestigVerwijderen() {
  bezig.value = true
  try {
    await api.contracten.verwijder(props.id)
    verwijderDialog.value = false
    toast.add({ severity: 'success', summary: 'Contract verwijderd', life: 3000 })
    router.push({ name: 'contract-lijst' })
  } catch (e) {
    verwijderDialog.value = false
    _toastFout(e)
  } finally {
    bezig.value = false
  }
}

onMounted(laad)
const typeLabel = (c) => label(CONTRACTTYPE, c)
</script>

<template>
  <section aria-labelledby="contract-detail-titel">
    <p v-if="fout" role="alert" data-testid="detail-fout" class="text-[var(--cd-color-danger)]">{{ fout }}</p>

    <template v-if="contract">
      <div class="flex items-center gap-[var(--cd-space-md)] mb-[var(--cd-space-md)]">
        <h1 id="contract-detail-titel" class="text-[length:var(--cd-text-2xl)] font-semibold text-[var(--cd-color-primary)]">
          {{ contract.contractnaam }}
        </h1>
        <Tag data-testid="detail-type" :value="typeLabel(contract.contracttype)" :severity="CONTRACTTYPE_SEVERITY[contract.contracttype] || 'info'" />
      </div>

      <dl class="card grid grid-cols-[max-content_1fr] gap-x-[var(--cd-space-lg)] gap-y-[var(--cd-space-sm)]">
        <dt class="font-semibold">Leverancier</dt>
        <dd>{{ contract.leverancier_naam }}</dd>
        <template v-if="contract.mantelcontract_id">
          <dt class="font-semibold">Mantelcontract</dt>
          <dd>
            <router-link
              :to="{ name: 'contract-detail', params: { id: contract.mantelcontract_id } }"
              data-testid="mantel-link"
              class="text-[var(--cd-color-primary)] hover:underline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--cd-color-primary)]"
            >
              Naar mantelcontract
            </router-link>
          </dd>
        </template>
        <dt class="font-semibold">Extern contract-ID</dt>
        <dd>{{ contract.extern_contract_id || '—' }}</dd>
        <dt class="font-semibold">Leverancier-kenmerk</dt>
        <dd>{{ contract.leverancier_contract_id || '—' }}</dd>
        <dt class="font-semibold">Begindatum</dt>
        <dd>{{ contract.begindatum || '—' }}</dd>
        <dt class="font-semibold">Einddatum</dt>
        <dd>{{ contract.einddatum || '—' }}</dd>
        <dt class="font-semibold">Vernieuwingsdatum</dt>
        <dd>{{ contract.vernieuwingsdatum || '—' }}</dd>
        <dt class="font-semibold">Dekking</dt>
        <dd data-testid="detail-dekking" class="flex flex-wrap gap-[var(--cd-space-xs)]">
          <Tag v-for="o in contract.dekking" :key="o.optie_sleutel" :value="o.label" :severity="o.actief ? 'info' : 'secondary'" />
          <span v-if="!contract.dekking?.length">—</span>
        </dd>
        <dt class="font-semibold">Kostenmodel</dt>
        <dd data-testid="detail-kostenmodel" class="flex flex-wrap gap-[var(--cd-space-xs)]">
          <Tag v-for="o in contract.kostenmodel" :key="o.optie_sleutel" :value="o.label" :severity="o.actief ? 'info' : 'secondary'" />
          <span v-if="!contract.kostenmodel?.length">—</span>
        </dd>
        <dt class="font-semibold">Omschrijving</dt>
        <dd class="whitespace-pre-wrap">{{ contract.omschrijving || '—' }}</dd>
        <dt class="font-semibold">Toelichting</dt>
        <dd class="whitespace-pre-wrap">{{ contract.toelichting || '—' }}</dd>
      </dl>

      <div class="mt-[var(--cd-space-lg)] flex flex-wrap gap-[var(--cd-space-md)]">
        <Button v-if="magBewerken" label="Bewerken" data-testid="bewerken-knop" @click="router.push({ name: 'contract-bewerken', params: { id: props.id } })" />
        <Button v-if="magVerwijderen" label="Verwijderen" severity="danger" data-testid="verwijder-knop" @click="verwijderDialog = true" />
      </div>
    </template>

    <Dialog v-model:visible="verwijderDialog" modal header="Contract verwijderen" data-testid="verwijder-dialog">
      <p class="mb-[var(--cd-space-md)] max-w-prose">
        Weet je zeker dat je <strong>{{ contract?.contractnaam }}</strong> wilt verwijderen? Een
        mantelcontract met deelcontracten of een aan applicaties gekoppeld contract kan niet
        worden verwijderd.
      </p>
      <div class="flex justify-end gap-[var(--cd-space-md)]">
        <Button label="Annuleren" severity="secondary" data-testid="verwijder-annuleer" @click="verwijderDialog = false" />
        <Button label="Definitief verwijderen" severity="danger" data-testid="verwijder-bevestig" :disabled="bezig" @click="bevestigVerwijderen" />
      </div>
    </Dialog>
  </section>
</template>
