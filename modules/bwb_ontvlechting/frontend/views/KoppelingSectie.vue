<script setup>
/**
 * KoppelingSectie — koppelingen van één applicatie (in ApplicatieDetail).
 *
 * Dialog-in-sectie (zie DatatypeSectie voor de motivatie). De API kent geen
 * "bron OF doel"-filter, dus twee disjuncte calls (DB-CHECK bron != doel →
 * geen overlap): Uitgaand (deze applicatie = bron) en Inkomend (= doel), elk met
 * eigen keyset-cursor en eigen "Meer laden". Bron/doel via applicatie-pickers;
 * bron == doel client-side geweigerd; bron/doel immutabel bij bewerken.
 */
import { computed, nextTick, reactive, ref } from 'vue'
import { Button, Column, DataTable, Dialog, Tag, Textarea, useToast } from '@/primevue'
import { useAuthStore } from '@/store/auth'
import { api } from '@/api'
import { IMPACT_SEVERITY, IMPACT_VERBREKING, KOPPELPROTOCOL, KOPPELRICHTING, label } from '../labels'

const props = defineProps({ applicatieId: { type: String, required: true } })
const auth = useAuthStore()
const toast = useToast()

const mag = computed(() => auth.hasRole('medewerker', 'beheerder'))

const uitgaand = reactive({ items: [], cursor: null, laden: false })
const inkomend = reactive({ items: [], cursor: null, laden: false })
const fout = ref(null)

const applicaties = ref([])
const appNaam = (id) => applicaties.value.find((a) => a.id === id)?.naam || id

const dialogOpen = ref(false)
const bewerkenId = ref(null)
const bezig = ref(false)
const opties = ref({ richting: [], protocol: [], impact_bij_verbreking: [] })
const form = reactive({
  bron_applicatie_id: '',
  doel_applicatie_id: '',
  richting: '',
  protocol: '',
  impact_bij_verbreking: '',
  omschrijving: '',
})
const fouten = reactive({})
const eersteVeld = ref(null)
let laatsteTrigger = null

function _toastFout(e) {
  const per = { 403: 'Geen rechten voor deze actie.', 404: 'Niet gevonden.', 409: e?.message || 'Deze koppeling bestaat al of is ongeldig.' }
  toast.add({ severity: 'error', summary: 'Fout', detail: per[e?.status] || e?.message || 'Er ging iets mis.', life: 5000 })
}

async function _laadRichting(state, params, reset) {
  state.laden = true
  try {
    const after = reset ? undefined : state.cursor
    const p = await api.koppelingen.lijst({ ...params, limit: 25, after })
    state.items = reset ? p.items : state.items.concat(p.items)
    state.cursor = p.volgende_cursor
  } catch (e) {
    fout.value = e?.message || 'Laden van koppelingen mislukt.'
  } finally {
    state.laden = false
  }
}
const laadUitgaand = (reset = false) => _laadRichting(uitgaand, { bronApplicatieId: props.applicatieId }, reset)
const laadInkomend = (reset = false) => _laadRichting(inkomend, { doelApplicatieId: props.applicatieId }, reset)
function laadBeide() {
  fout.value = null
  laadUitgaand(true)
  laadInkomend(true)
}

async function _laadOptiesEenmalig() {
  if (!opties.value.richting.length) {
    try {
      opties.value = await api.koppelingen.opties()
    } catch (e) {
      _toastFout(e)
    }
  }
  if (!applicaties.value.length) {
    try {
      const p = await api.applicaties.lijst({ limit: 100 })
      applicaties.value = p.items
    } catch (e) {
      _toastFout(e)
    }
  }
}

function _reset() {
  Object.assign(form, {
    bron_applicatie_id: props.applicatieId, // default: deze applicatie als bron
    doel_applicatie_id: '',
    richting: '',
    protocol: '',
    impact_bij_verbreking: '',
    omschrijving: '',
  })
  Object.keys(fouten).forEach((k) => delete fouten[k])
}

async function openNieuw(e) {
  laatsteTrigger = e?.currentTarget ?? null
  bewerkenId.value = null
  await _laadOptiesEenmalig()
  _reset()
  dialogOpen.value = true
}

async function openBewerken(e, rij) {
  laatsteTrigger = e?.currentTarget ?? null
  bewerkenId.value = rij.id
  await _laadOptiesEenmalig()
  Object.keys(fouten).forEach((k) => delete fouten[k])
  Object.assign(form, {
    bron_applicatie_id: rij.bron_applicatie_id,
    doel_applicatie_id: rij.doel_applicatie_id,
    richting: rij.richting,
    protocol: rij.protocol,
    impact_bij_verbreking: rij.impact_bij_verbreking,
    omschrijving: rij.omschrijving || '',
  })
  dialogOpen.value = true
}

function focusEerste() {
  // Ná de focustrap van PrimeVue Dialog (die anders de sluitknop focust).
  setTimeout(() => {
    const el = eersteVeld.value?.$el ?? eersteVeld.value
    el?.focus?.()
  }, 0)
}
function onHide() {
  laatsteTrigger?.focus?.()
}

function valideer() {
  Object.keys(fouten).forEach((k) => delete fouten[k])
  if (!form.bron_applicatie_id) fouten.bron_applicatie_id = 'Kies een bron-applicatie.'
  if (!form.doel_applicatie_id) fouten.doel_applicatie_id = 'Kies een doel-applicatie.'
  if (form.bron_applicatie_id && form.bron_applicatie_id === form.doel_applicatie_id)
    fouten.doel_applicatie_id = 'Bron en doel moeten verschillen.'
  for (const v of ['richting', 'protocol', 'impact_bij_verbreking']) if (!form[v]) fouten[v] = 'Maak een keuze.'
  return Object.keys(fouten).length === 0
}

function _serverveldfouten(e) {
  if (e?.status === 422 && Array.isArray(e.detail)) {
    let t = false
    for (const d of e.detail) {
      const v = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : null
      if (v && v in form) {
        fouten[v] = d.msg || 'Ongeldige waarde.'
        t = true
      }
    }
    return t
  }
  return false
}

async function opslaan() {
  if (!valideer()) return
  bezig.value = true
  try {
    if (bewerkenId.value) {
      // bron/doel immutabel → niet meesturen
      await api.koppelingen.werkBij(bewerkenId.value, {
        richting: form.richting,
        protocol: form.protocol,
        impact_bij_verbreking: form.impact_bij_verbreking,
        omschrijving: form.omschrijving.trim() || null,
      })
    } else {
      await api.koppelingen.maak({
        bron_applicatie_id: form.bron_applicatie_id,
        doel_applicatie_id: form.doel_applicatie_id,
        richting: form.richting,
        protocol: form.protocol,
        impact_bij_verbreking: form.impact_bij_verbreking,
        omschrijving: form.omschrijving.trim() || null,
      })
    }
    toast.add({ severity: 'success', summary: bewerkenId.value ? 'Opgeslagen' : 'Toegevoegd', life: 3000 })
    dialogOpen.value = false
    laadBeide() // ververs beide richtingen (relevante richting is altijd inbegrepen)
  } catch (e) {
    if (!_serverveldfouten(e)) _toastFout(e)
  } finally {
    bezig.value = false
  }
}

const verwijderOpen = ref(false)
const teVerwijderen = ref(null)
function vraagVerwijder(e, rij) {
  laatsteTrigger = e?.currentTarget ?? null
  teVerwijderen.value = rij
  verwijderOpen.value = true
}
async function bevestigVerwijder() {
  bezig.value = true
  try {
    await api.koppelingen.verwijder(teVerwijderen.value.id)
    toast.add({ severity: 'success', summary: 'Verwijderd', life: 3000 })
    verwijderOpen.value = false
    laadBeide()
  } catch (e) {
    _toastFout(e)
  } finally {
    bezig.value = false
  }
}

laadBeide()
</script>

<template>
  <section class="card" aria-labelledby="sectie-koppelingen">
    <div class="flex items-center gap-[var(--cd-space-md)] mb-[var(--cd-space-sm)]">
      <h2 id="sectie-koppelingen" class="text-[length:var(--cd-text-lg)] font-semibold">Koppelingen</h2>
      <Button v-if="mag" label="Toevoegen" size="small" data-testid="kp-toevoegen" class="ml-auto" @click="openNieuw" />
    </div>

    <p v-if="fout" role="alert" data-testid="kp-fout" class="text-[var(--cd-color-danger)] mb-[var(--cd-space-sm)]">{{ fout }}</p>

    <!-- Uitgaand: deze applicatie = bron -->
    <h3 class="font-semibold mt-[var(--cd-space-sm)]">Uitgaand (deze applicatie is bron)</h3>
    <DataTable :value="uitgaand.items" data-testid="kp-tabel-uitgaand">
      <Column header="Rol"><template #body>Bron</template></Column>
      <Column header="Tegenpartij (doel)"><template #body="{ data }">{{ appNaam(data.doel_applicatie_id) }}</template></Column>
      <Column header="Richting"><template #body="{ data }"><Tag :value="label(KOPPELRICHTING, data.richting)" /></template></Column>
      <Column header="Protocol"><template #body="{ data }">{{ label(KOPPELPROTOCOL, data.protocol) }}</template></Column>
      <Column header="Impact"><template #body="{ data }"><Tag :value="label(IMPACT_VERBREKING, data.impact_bij_verbreking)" :severity="IMPACT_SEVERITY[data.impact_bij_verbreking] || 'info'" /></template></Column>
      <Column header="">
        <template #body="{ data }">
          <div v-if="mag" class="flex gap-[var(--cd-space-sm)]">
            <Button label="Bewerken" size="small" severity="secondary" :data-testid="`kp-bewerk-${data.id}`" @click="(e) => openBewerken(e, data)" />
            <Button label="Verwijderen" size="small" severity="danger" :data-testid="`kp-verwijder-${data.id}`" @click="(e) => vraagVerwijder(e, data)" />
          </div>
        </template>
      </Column>
      <template #empty><span data-testid="kp-leeg-uitgaand">Geen uitgaande koppelingen.</span></template>
    </DataTable>
    <Button v-if="uitgaand.cursor" label="Meer laden" size="small" severity="secondary" data-testid="kp-meer-uitgaand" :disabled="uitgaand.laden" class="mt-[var(--cd-space-sm)]" @click="laadUitgaand()" />

    <!-- Inkomend: deze applicatie = doel -->
    <h3 class="font-semibold mt-[var(--cd-space-md)]">Inkomend (deze applicatie is doel)</h3>
    <DataTable :value="inkomend.items" data-testid="kp-tabel-inkomend">
      <Column header="Rol"><template #body>Doel</template></Column>
      <Column header="Tegenpartij (bron)"><template #body="{ data }">{{ appNaam(data.bron_applicatie_id) }}</template></Column>
      <Column header="Richting"><template #body="{ data }"><Tag :value="label(KOPPELRICHTING, data.richting)" /></template></Column>
      <Column header="Protocol"><template #body="{ data }">{{ label(KOPPELPROTOCOL, data.protocol) }}</template></Column>
      <Column header="Impact"><template #body="{ data }"><Tag :value="label(IMPACT_VERBREKING, data.impact_bij_verbreking)" :severity="IMPACT_SEVERITY[data.impact_bij_verbreking] || 'info'" /></template></Column>
      <Column header="">
        <template #body="{ data }">
          <div v-if="mag" class="flex gap-[var(--cd-space-sm)]">
            <Button label="Bewerken" size="small" severity="secondary" :data-testid="`kp-bewerk-${data.id}`" @click="(e) => openBewerken(e, data)" />
            <Button label="Verwijderen" size="small" severity="danger" :data-testid="`kp-verwijder-${data.id}`" @click="(e) => vraagVerwijder(e, data)" />
          </div>
        </template>
      </Column>
      <template #empty><span data-testid="kp-leeg-inkomend">Geen inkomende koppelingen.</span></template>
    </DataTable>
    <Button v-if="inkomend.cursor" label="Meer laden" size="small" severity="secondary" data-testid="kp-meer-inkomend" :disabled="inkomend.laden" class="mt-[var(--cd-space-sm)]" @click="laadInkomend()" />

    <!-- Aanmaken/bewerken -->
    <Dialog v-model:visible="dialogOpen" modal :closable="false" :header="bewerkenId ? 'Koppeling bewerken' : 'Koppeling toevoegen'" data-testid="kp-dialog" @show="focusEerste" @hide="onHide">
      <form class="flex flex-col gap-[var(--cd-space-md)] min-w-[22rem]" data-testid="kp-form" @submit.prevent="opslaan">
        <div class="flex flex-col gap-[var(--cd-space-xs)]">
          <label for="kp-bron" class="font-semibold">Bron-applicatie *</label>
          <select id="kp-bron" ref="eersteVeld" autofocus v-model="form.bron_applicatie_id" :disabled="!!bewerkenId" data-testid="kp-veld-bron" :aria-invalid="!!fouten.bron_applicatie_id" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-[var(--cd-space-xs)] bg-white disabled:opacity-60">
            <option value="" disabled>— kies —</option>
            <option v-for="a in applicaties" :key="a.id" :value="a.id">{{ a.naam }}</option>
          </select>
          <span v-if="fouten.bron_applicatie_id" role="alert" data-testid="kp-fout-bron" class="text-[var(--cd-color-danger)] text-[length:var(--cd-text-sm)]">{{ fouten.bron_applicatie_id }}</span>
        </div>
        <div class="flex flex-col gap-[var(--cd-space-xs)]">
          <label for="kp-doel" class="font-semibold">Doel-applicatie *</label>
          <select id="kp-doel" v-model="form.doel_applicatie_id" :disabled="!!bewerkenId" data-testid="kp-veld-doel" :aria-invalid="!!fouten.doel_applicatie_id" aria-describedby="kp-fout-doel" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-[var(--cd-space-xs)] bg-white disabled:opacity-60">
            <option value="" disabled>— kies —</option>
            <option v-for="a in applicaties" :key="a.id" :value="a.id">{{ a.naam }}</option>
          </select>
          <span v-if="fouten.doel_applicatie_id" id="kp-fout-doel" role="alert" data-testid="kp-fout-doel" class="text-[var(--cd-color-danger)] text-[length:var(--cd-text-sm)]">{{ fouten.doel_applicatie_id }}</span>
        </div>
        <div v-for="veld in ['richting', 'protocol', 'impact_bij_verbreking']" :key="veld" class="flex flex-col gap-[var(--cd-space-xs)]">
          <label :for="`kp-${veld}`" class="font-semibold capitalize">{{ veld.replace(/_/g, ' ') }} *</label>
          <select :id="`kp-${veld}`" v-model="form[veld]" :data-testid="`kp-veld-${veld}`" :aria-invalid="!!fouten[veld]" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-[var(--cd-space-xs)] bg-white">
            <option value="" disabled>— maak een keuze —</option>
            <option v-for="c in opties[veld]" :key="c" :value="c">{{ c.replace(/_/g, ' ') }}</option>
          </select>
          <span v-if="fouten[veld]" role="alert" :data-testid="`kp-fout-${veld}`" class="text-[var(--cd-color-danger)] text-[length:var(--cd-text-sm)]">{{ fouten[veld] }}</span>
        </div>
        <div class="flex flex-col gap-[var(--cd-space-xs)]">
          <label for="kp-omschrijving" class="font-semibold">Omschrijving</label>
          <Textarea id="kp-omschrijving" v-model="form.omschrijving" rows="3" data-testid="kp-veld-omschrijving" />
        </div>
        <div class="flex gap-[var(--cd-space-md)]">
          <Button type="submit" label="Opslaan" data-testid="kp-opslaan" :disabled="bezig" />
          <Button type="button" label="Annuleren" severity="secondary" @click="dialogOpen = false" />
        </div>
      </form>
    </Dialog>

    <Dialog v-model:visible="verwijderOpen" modal header="Koppeling verwijderen" data-testid="kp-verwijder-dialog" @hide="onHide">
      <p class="mb-[var(--cd-space-md)] max-w-prose">Deze koppeling definitief verwijderen?</p>
      <div class="flex justify-end gap-[var(--cd-space-md)]">
        <Button label="Annuleren" severity="secondary" @click="verwijderOpen = false" />
        <Button label="Verwijderen" severity="danger" data-testid="kp-verwijder-bevestig" :disabled="bezig" @click="bevestigVerwijder" />
      </div>
    </Dialog>
  </section>
</template>
