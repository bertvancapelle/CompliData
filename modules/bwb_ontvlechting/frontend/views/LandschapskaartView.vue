<script setup>
/**
 * LandschapskaartView v3 — interactieve landschapskaart op Cytoscape.js (ADR-025).
 *
 * Drie modi (Ego / Impact / Geheel model), zoeken + vier filters (domein/leverancier/hosting/
 * lifecycle), actieve migratieset, node-detail met doorklik naar het applicatie-detail, en een
 * lifecycle-legenda. De Cytoscape-graaf is een afgeleide van de reactieve state (tekenGraaf());
 * álle panelen (zoek/resultaten/set/detail/legenda/samenvatting) zijn pure Vue-state, zodat de
 * UI testbaar is met een gemockte cytoscape. Read-only; geen engine-aanraking.
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from '@/composables/router'
import cytoscape from '@/composables/cytoscape'
import { api } from '@/api'
import { humaniseer } from '../labels'

const router = useRouter()

// Lifecycle → kleur (node-achtergrond + rand).
const LC_STYLE = {
  migratieklaar: { bg: '#dcfce7', border: '#22c55e' },
  geblokkeerd: { bg: '#fee2e2', border: '#ef4444' },
  in_inventarisatie: { bg: '#dbeafe', border: '#3b82f6' },
  concept: { bg: '#f1f5f9', border: '#94a3b8' },
  null: { bg: '#f8fafc', border: '#cbd5e1' },
}
const lcStyle = (s) => LC_STYLE[s] || LC_STYLE.null
const LIFECYCLE_OPTIES = ['migratieklaar', 'in_inventarisatie', 'geblokkeerd', 'concept']
const RINGEN = ['applicaties', 'beheerorganisatie', 'contracten', 'infrastructuur']
const INSET = { bg: '#1e3a8a', border: '#1e3a8a' }
const RAAKVLAK = { bg: '#fed7aa', border: '#ea580c' }
// Deterministische domeinkleuren (border in "kleur op domein"-modus).
const DOMEIN_PALET = ['#2563eb', '#d97706', '#0891b2', '#7c3aed', '#16a34a', '#db2777', '#65a30d', '#dc2626']

// ── State ───────────────────────────────────────────────────────────────────────
const nodes = ref([])
const edges = ref([])
const laden = ref(true)
const fout = ref(null)

const modus = ref('ego') // 'ego' | 'impact' | 'geheel'
const zoekterm = ref('')
const filterDomein = ref('')
const filterLeverancier = ref('')
const filterHosting = ref('')
const filterLifecycle = ref('')
const ringAan = ref(new Set(RINGEN))
const actieveSet = ref(new Set())
const egoStartId = ref(null)
const detailId = ref(null)
const opbouwModus = ref(true) // geheel-model: true=insluiten (begint leeg), false=afpellen (begint vol)
const kleurOpDomein = ref(false)
const verbergOnverbonden = ref(false)

const containerRef = ref(null)
let cy = null

const nodePerId = computed(() => Object.fromEntries(nodes.value.map((n) => [n.id, n])))
const heeftData = computed(() => nodes.value.length > 0)
const isApplicatie = (n) => n?.element_type === 'applicatie'

// ── Data laden ────────────────────────────────────────────────────────────────
async function laad() {
  laden.value = true
  fout.value = null
  try {
    const data = await api.landschapskaart.haalGrafdata()
    nodes.value = data.nodes || []
    edges.value = data.edges || []
    const eersteApp = nodes.value.find(isApplicatie)
    egoStartId.value = eersteApp ? eersteApp.id : null
  } catch (e) {
    fout.value = e?.message || 'Laden van de landschapskaart mislukt.'
  } finally {
    laden.value = false
  }
}

// Alleen applicaties zijn selecteerbaar via de zoeklijst/filters/actieve set; partijen,
// contracten en infrastructuur verschijnen automatisch als ring-nodes rond de gekozen apps.
const _isApp = (n) => n?.element_type === 'applicatie' || (n?.element_type === 'component' && n?.laag === 'application')
const appNodes = computed(() => nodes.value.filter(_isApp))

// ── Filter-opties (datagedreven; alleen uit de applicaties) ──────────────────────
const _uniek = (sel) => [...new Set(appNodes.value.map(sel).filter(Boolean))].sort()
const domeinOpties = computed(() => _uniek((n) => n.domein))
const leverancierOpties = computed(() => _uniek((n) => n.leverancier_naam))
const hostingOpties = computed(() => _uniek((n) => n.hosting_model))
const domeinKleur = computed(() => Object.fromEntries(domeinOpties.value.map((d, i) => [d, DOMEIN_PALET[i % DOMEIN_PALET.length]])))

// ── Zoeken + filteren ─────────────────────────────────────────────────────────
const filterActief = computed(
  () => !!(zoekterm.value.trim() || filterDomein.value || filterLeverancier.value || filterHosting.value || filterLifecycle.value),
)
function _matcht(n) {
  const q = zoekterm.value.trim().toLowerCase()
  if (q && !`${n.naam || ''} ${n.domein || ''} ${n.leverancier_naam || ''}`.toLowerCase().includes(q)) return false
  if (filterDomein.value && n.domein !== filterDomein.value) return false
  if (filterLeverancier.value && n.leverancier_naam !== filterLeverancier.value) return false
  if (filterHosting.value && n.hosting_model !== filterHosting.value) return false
  if (filterLifecycle.value && n.lifecycle_status !== filterLifecycle.value) return false
  return true
}
const gefilterdeNodes = computed(() => appNodes.value.filter(_matcht))

// ── Zichtbare nodes/edges per modus ──────────────────────────────────────────────
const egoBuren = computed(() => {
  const sp = egoStartId.value
  const ids = new Set()
  if (sp) {
    for (const e of edges.value) {
      if (!ringAan.value.has(e.ring)) continue
      if (e.bron_id === sp) ids.add(e.doel_id)
      else if (e.doel_id === sp) ids.add(e.bron_id)
    }
  }
  return ids
})
const zichtbareNodes = computed(() => {
  if (modus.value === 'ego') {
    const sp = egoStartId.value
    return nodes.value.filter((n) => n.id === sp || egoBuren.value.has(n.id))
  }
  if (modus.value === 'impact') return nodes.value.filter(isApplicatie)
  // geheel model: opbouw = alleen de match (begint leeg); afpel = alles behalve de match (begint vol)
  if (!filterActief.value) return opbouwModus.value ? [] : nodes.value
  const match = new Set(gefilterdeNodes.value.map((n) => n.id))
  return nodes.value.filter((n) => (opbouwModus.value ? match.has(n.id) : !match.has(n.id)))
})
const zichtbareNodeIds = computed(() => new Set(zichtbareNodes.value.map((n) => n.id)))
const zichtbareEdges = computed(() =>
  edges.value.filter(
    (e) => zichtbareNodeIds.value.has(e.bron_id) && zichtbareNodeIds.value.has(e.doel_id) && (modus.value !== 'ego' && modus.value !== 'geheel' ? true : ringAan.value.has(e.ring)),
  ),
)

// ── Impact-berekening ───────────────────────────────────────────────────────────
const flowEdges = computed(() => edges.value.filter((e) => e.ring === 'applicaties'))
const grensEdges = computed(() => flowEdges.value.filter((e) => actieveSet.value.has(e.bron_id) !== actieveSet.value.has(e.doel_id)))
const raakvlakken = computed(() => {
  const s = new Set()
  for (const e of grensEdges.value) {
    if (!actieveSet.value.has(e.bron_id)) s.add(e.bron_id)
    if (!actieveSet.value.has(e.doel_id)) s.add(e.doel_id)
  }
  return s
})
const impactSamenvatting = computed(
  () => `${actieveSet.value.size} in set · ${raakvlakken.value.size} raakvlakken · ${grensEdges.value.length} grensoverschrijdende koppelingen`,
)

// ── Actieve set ─────────────────────────────────────────────────────────────────
function inSet(id) {
  return actieveSet.value.has(id)
}
function toggleSet(id) {
  const s = new Set(actieveSet.value)
  s.has(id) ? s.delete(id) : s.add(id)
  actieveSet.value = s
}
function voegAlleGefilterdeToe() {
  const s = new Set(actieveSet.value)
  for (const n of gefilterdeNodes.value) s.add(n.id)
  actieveSet.value = s
}
const actieveSetNodes = computed(() => [...actieveSet.value].map((id) => nodePerId.value[id]).filter(Boolean))

// ── Detail ────────────────────────────────────────────────────────────────────
const detailNode = computed(() => (detailId.value ? nodePerId.value[detailId.value] : null))
const detailKoppelingen = computed(() => {
  const id = detailId.value
  if (!id) return 0
  return edges.value.filter((e) => e.bron_id === id || e.doel_id === id).length
})
function selecteerNode(id) {
  detailId.value = id
  // In ego-modus hercentreert een applicatie-klik.
  if (modus.value === 'ego' && isApplicatie(nodePerId.value[id])) egoStartId.value = id
}
function openApplicatie() {
  if (detailNode.value) router.push({ name: 'applicatie-detail', params: { id: detailNode.value.id } })
}

// ── Cytoscape-graaf (afgeleide van de state) ─────────────────────────────────────
const hostingIcoon = (h) => (h === 'saas' ? '☁' : '🏢')

function _nodeData(n) {
  let bg = lcStyle(n.lifecycle_status).bg
  let border = kleurOpDomein.value && n.domein ? domeinKleur.value[n.domein] : lcStyle(n.lifecycle_status).border
  if (modus.value === 'impact') {
    if (inSet(n.id)) ({ bg, border } = INSET)
    else if (raakvlakken.value.has(n.id)) ({ bg, border } = RAAKVLAK)
  }
  return { id: n.id, label: (n.naam || '') + (n.blokkades_open > 0 ? ' ⚠' : ''), bg, border }
}
function _edgeData(e, i) {
  let lc = '#cbd5e1'
  let w = 1.5
  let ls = 'solid'
  if (modus.value === 'impact' && e.ring === 'applicaties') {
    const grens = actieveSet.value.has(e.bron_id) !== actieveSet.value.has(e.doel_id)
    const beide = actieveSet.value.has(e.bron_id) && actieveSet.value.has(e.doel_id)
    lc = grens ? '#ea580c' : beide ? '#2563eb' : '#cbd5e1'
    w = grens ? 3 : 2
  }
  return { id: `e${i}-${e.bron_id}-${e.doel_id}-${e.relatietype}`, source: e.bron_id, target: e.doel_id, lc, w, ls }
}
function _elementen() {
  let zn = zichtbareNodes.value
  let ze = zichtbareEdges.value
  if (verbergOnverbonden.value) {
    const verbonden = new Set()
    ze.forEach((e) => {
      verbonden.add(e.bron_id)
      verbonden.add(e.doel_id)
    })
    zn = zn.filter((n) => verbonden.has(n.id))
  }
  const znIds = new Set(zn.map((n) => n.id))
  ze = ze.filter((e) => znIds.has(e.bron_id) && znIds.has(e.doel_id))
  return [
    ...zn.map((n) => ({ data: _nodeData(n) })),
    ...ze.map((e, i) => ({ data: _edgeData(e, i) })),
  ]
}
const zichtbaarAantal = computed(() => {
  // Telling die het canvas toont (na evt. verberg-onverbonden) — testbaar zonder cy.
  if (!verbergOnverbonden.value) return zichtbareNodes.value.length
  const verbonden = new Set()
  zichtbareEdges.value.forEach((e) => {
    verbonden.add(e.bron_id)
    verbonden.add(e.doel_id)
  })
  return zichtbareNodes.value.filter((n) => verbonden.has(n.id)).length
})

function _layout() {
  if (modus.value === 'ego') return { name: 'concentric', concentric: (n) => (n.id() === egoStartId.value ? 10 : 5), levelWidth: () => 1, minNodeSpacing: 40 }
  return { name: 'cose', animate: false, padding: 30, nodeRepulsion: modus.value === 'geheel' ? 12000 : 6000 }
}
async function tekenGraaf() {
  if (!cy) return
  await nextTick()
  await nextTick() // tweede tick voor (HMR-)edge cases waarin de layout nog niet geflusht is
  // Cytoscape meet zijn container soms op 0 (flex-hoogte nog niet gezet) → forceer een hoogte
  // zodat de graaf nooit op 0px initialiseert en zichtbaar blijft i.p.v. leeg.
  const el = containerRef.value
  if (el && el.offsetHeight === 0) el.style.minHeight = '500px'
  cy.elements().remove()
  cy.add(_elementen())
  cy.layout(_layout()).run()
  // Klein delay voor de browser-layout-flush, dán her-meten + passend maken.
  setTimeout(() => {
    cy?.resize?.()
    cy?.fit?.(undefined, 50)
  }, 100)
}

const CY_STYLE = [
  {
    selector: 'node',
    style: {
      'background-color': 'data(bg)', 'border-color': 'data(border)', 'border-width': 2,
      label: 'data(label)', 'font-size': 9, 'text-valign': 'center', 'text-halign': 'center',
      width: 78, height: 28, shape: 'round-rectangle', 'text-wrap': 'ellipsis', 'text-max-width': 70,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 'data(w)', 'line-color': 'data(lc)', 'line-style': 'data(ls)',
      'target-arrow-shape': 'triangle', 'target-arrow-color': 'data(lc)', 'curve-style': 'bezier',
    },
  },
]

let resizeObserver = null

onMounted(async () => {
  await laad()
  await nextTick() // wacht tot de canvas-div in de DOM staat (en de flex-hoogte gezet is)
  if (containerRef.value) {
    cy = cytoscape({ container: containerRef.value, elements: [], style: CY_STYLE })
    cy.on('tap', 'node', (evt) => selecteerNode(evt.target.id()))
    tekenGraaf()
    // Her-meten + passend maken bij containerwijzigingen (modus-wissel, sidebar, venster-resize).
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        cy?.resize?.()
        cy?.fit?.(undefined, 50)
      })
      resizeObserver.observe(containerRef.value)
    }
  }
})
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  cy?.destroy?.()
})

// Hertekenen bij elke state die de graaf raakt.
watch(
  [modus, zichtbareNodes, zichtbareEdges, actieveSet, kleurOpDomein, verbergOnverbonden],
  () => tekenGraaf(),
  { deep: false },
)

function centreer() {
  cy?.fit?.()
}
function toggleRing(r) {
  const s = new Set(ringAan.value)
  s.has(r) ? s.delete(r) : s.add(r)
  ringAan.value = s
}
const typeLabel = (t) => humaniseer(t)
</script>

<template>
  <div class="flex w-full flex-col" data-testid="lk-wrapper" style="height: calc(100vh - 9rem)">
    <!-- Topbar: modus-toggle -->
    <div class="flex items-center gap-[var(--cd-space-sm)] border-b border-[var(--cd-color-border)] bg-white p-[var(--cd-space-sm)]">
      <div class="flex gap-1 rounded-[var(--cd-radius-btn)] bg-[var(--cd-color-accent)] p-1">
        <button v-for="m in ['ego', 'impact', 'geheel']" :key="m" type="button" :data-testid="`lk-modus-${m}`" :aria-pressed="modus === m" :class="['rounded-[var(--cd-radius-btn)] px-[var(--cd-space-md)] py-1 text-[length:var(--cd-text-sm)]', modus === m ? 'bg-[var(--cd-color-primary)] text-white' : '']" @click="modus = m">
          {{ m === 'ego' ? 'Ego-view' : m === 'impact' ? 'Impact-view' : 'Geheel model' }}
        </button>
      </div>
      <span class="ml-auto text-[length:var(--cd-text-sm)] text-[var(--cd-color-text-muted)]" data-testid="lk-zichtbaar-aantal">{{ zichtbaarAantal }} nodes zichtbaar</span>
    </div>

    <div class="flex min-h-0 flex-1">
      <!-- Linkerpaneel: zoek + filters + resultaten -->
      <aside class="flex w-60 flex-shrink-0 flex-col gap-[var(--cd-space-sm)] overflow-y-auto border-r border-[var(--cd-color-border)] bg-white p-[var(--cd-space-md)]" data-testid="lk-links">
        <input v-model="zoekterm" type="search" data-testid="lk-zoek" placeholder="🔍 Zoek naam/domein/leverancier…" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-1 text-[length:var(--cd-text-sm)]" />

        <select v-model="filterDomein" data-testid="lk-filter-domein" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-1 text-[length:var(--cd-text-sm)]">
          <option value="">Alle domeinen</option>
          <option v-for="d in domeinOpties" :key="d" :value="d">{{ typeLabel(d) }}</option>
        </select>
        <select v-model="filterLeverancier" data-testid="lk-filter-leverancier" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-1 text-[length:var(--cd-text-sm)]">
          <option value="">Alle leveranciers</option>
          <option v-for="l in leverancierOpties" :key="l" :value="l">{{ l }}</option>
        </select>
        <select v-model="filterHosting" data-testid="lk-filter-hosting" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-1 text-[length:var(--cd-text-sm)]">
          <option value="">Alle hosting</option>
          <option v-for="h in hostingOpties" :key="h" :value="h">{{ typeLabel(h) }}</option>
        </select>
        <select v-model="filterLifecycle" data-testid="lk-filter-lifecycle" class="rounded-[var(--cd-radius-input)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-1 text-[length:var(--cd-text-sm)]">
          <option value="">Alle lifecycle</option>
          <option v-for="lc in LIFECYCLE_OPTIES" :key="lc" :value="lc">{{ typeLabel(lc) }}</option>
        </select>

        <label v-if="modus === 'geheel'" class="flex items-center gap-2 text-[length:var(--cd-text-sm)]">
          <input type="checkbox" :checked="!opbouwModus" data-testid="lk-afpel-toggle" @change="opbouwModus = !opbouwModus" />Afpel-modus (begint vol)
        </label>

        <template v-if="modus === 'ego'">
          <p class="font-semibold text-[length:var(--cd-text-sm)]">Ringen</p>
          <label v-for="r in RINGEN" :key="r" class="flex items-center gap-2 text-[length:var(--cd-text-sm)]">
            <input type="checkbox" :checked="ringAan.has(r)" :data-testid="`lk-ring-${r}`" @change="toggleRing(r)" />{{ typeLabel(r) }}
          </label>
        </template>

        <p class="mt-[var(--cd-space-sm)] font-semibold text-[length:var(--cd-text-sm)]">Resultaten ({{ gefilterdeNodes.length }})</p>
        <ul class="flex flex-col gap-1" data-testid="lk-resultaten">
          <li v-for="n in gefilterdeNodes" :key="n.id" :data-testid="`lk-res-${n.id}`" :class="['flex items-center gap-1 rounded px-1 py-0.5 text-[length:var(--cd-text-sm)]', inSet(n.id) ? 'bg-[var(--cd-color-accent)]' : '']">
            <span class="inline-block h-3 w-3 shrink-0 rounded-full" :style="{ background: lcStyle(n.lifecycle_status).bg, border: `1px solid ${lcStyle(n.lifecycle_status).border}` }"></span>
            <button type="button" class="grow truncate text-left hover:underline" :data-testid="`lk-res-naam-${n.id}`" @click="selecteerNode(n.id)">{{ n.naam }}</button>
            <span v-if="n.blokkades_open > 0" :data-testid="`lk-res-blok-${n.id}`" title="Open blokkade(s)">⚠</span>
            <span v-if="n.hosting_model">{{ hostingIcoon(n.hosting_model) }}</span>
            <button type="button" class="text-[var(--cd-color-primary)]" :data-testid="`lk-res-set-${n.id}`" @click="toggleSet(n.id)">{{ inSet(n.id) ? '×' : '+' }}</button>
          </li>
          <li v-if="!gefilterdeNodes.length" class="text-[length:var(--cd-text-xs)] text-[var(--cd-color-text-muted)]">Geen resultaten.</li>
        </ul>
        <button type="button" data-testid="lk-voeg-alle" class="mt-1 rounded-[var(--cd-radius-btn)] bg-[var(--cd-color-primary)] px-[var(--cd-space-sm)] py-1 text-[length:var(--cd-text-sm)] text-white" @click="voegAlleGefilterdeToe">+ Voeg alle gefilterde toe</button>
      </aside>

      <!-- Canvas — min-h-0 is kritiek: zonder negeert een flex-child de height:100% van de parent,
           waardoor Cytoscape op hoogte 0 initialiseert en de graaf leeg/onzichtbaar blijft. -->
      <div class="relative min-h-0 min-w-0 flex-1 bg-[var(--cd-color-surface)]">
        <!-- Inline min-height als harde vangrail: zelfs als de flex-hoogteketen faalt, krijgt
             Cytoscape een meetbare hoogte op het init-moment (anders blijft de graaf leeg). -->
        <div ref="containerRef" data-testid="lk-canvas" class="h-full w-full" style="min-height: 500px"></div>

        <!-- Tools (rechtsboven) -->
        <div class="absolute right-3 top-3 z-10 flex gap-1">
          <button type="button" data-testid="lk-centreer" class="rounded-[var(--cd-radius-btn)] bg-white/90 px-2 py-1 text-[length:var(--cd-text-sm)] shadow-[var(--cd-shadow-sm)]" @click="centreer">⊡ Centreer</button>
          <button type="button" data-testid="lk-kleur-domein" :aria-pressed="kleurOpDomein" :class="['rounded-[var(--cd-radius-btn)] px-2 py-1 text-[length:var(--cd-text-sm)] shadow-[var(--cd-shadow-sm)]', kleurOpDomein ? 'bg-[var(--cd-color-primary)] text-white' : 'bg-white/90']" @click="kleurOpDomein = !kleurOpDomein">Kleur op domein</button>
          <button type="button" data-testid="lk-verberg-onverbonden" :aria-pressed="verbergOnverbonden" :class="['rounded-[var(--cd-radius-btn)] px-2 py-1 text-[length:var(--cd-text-sm)] shadow-[var(--cd-shadow-sm)]', verbergOnverbonden ? 'bg-[var(--cd-color-primary)] text-white' : 'bg-white/90']" @click="verbergOnverbonden = !verbergOnverbonden">Verberg los</button>
        </div>

        <!-- Impact-samenvatting (overlay onderaan) -->
        <p v-if="modus === 'impact'" data-testid="impact-samenvatting" class="absolute bottom-3 left-1/2 z-10 -translate-x-1/2 rounded-full bg-white px-[var(--cd-space-md)] py-1 text-[length:var(--cd-text-sm)] font-semibold shadow-[var(--cd-shadow-md)]">{{ impactSamenvatting }}</p>

        <p v-if="laden" data-testid="lk-laden" class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[var(--cd-color-text-muted)]">Landschap laden…</p>
        <p v-else-if="fout" role="alert" data-testid="lk-fout" class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[var(--cd-color-danger)]">{{ fout }}</p>
        <p v-else-if="!heeftData" data-testid="lk-leeg" class="absolute left-1/2 top-1/2 max-w-md -translate-x-1/2 -translate-y-1/2 text-center text-[var(--cd-color-text-muted)]">Nog geen landschapsdata geregistreerd.</p>
      </div>

      <!-- Rechterpaneel: actieve set + detail + legenda -->
      <aside class="flex w-56 flex-shrink-0 flex-col gap-[var(--cd-space-md)] overflow-y-auto border-l border-[var(--cd-color-border)] bg-white p-[var(--cd-space-md)]" data-testid="lk-rechts">
        <div>
          <p class="mb-1 font-semibold text-[length:var(--cd-text-sm)]">Actieve set ({{ actieveSet.size }})</p>
          <ul class="flex max-h-40 flex-col gap-1 overflow-y-auto" data-testid="lk-set">
            <li v-for="n in actieveSetNodes" :key="n.id" :data-testid="`lk-set-${n.id}`" class="flex items-center gap-1 text-[length:var(--cd-text-sm)]">
              <span class="inline-block h-3 w-3 shrink-0 rounded-full" :style="{ background: lcStyle(n.lifecycle_status).bg }"></span>
              <button type="button" class="grow truncate text-left hover:underline" @click="selecteerNode(n.id)">{{ n.naam }}</button>
              <span v-if="n.blokkades_open > 0">⚠</span>
              <button type="button" class="text-[var(--cd-color-danger)]" :data-testid="`lk-set-verwijder-${n.id}`" @click="toggleSet(n.id)">×</button>
            </li>
            <li v-if="!actieveSet.size" class="text-[length:var(--cd-text-xs)] text-[var(--cd-color-text-muted)]">Nog niets geselecteerd.</li>
          </ul>
        </div>

        <div class="border-t border-[var(--cd-color-border)] pt-[var(--cd-space-sm)]">
          <p class="mb-1 font-semibold text-[length:var(--cd-text-sm)]">Detail</p>
          <div v-if="detailNode" data-testid="lk-detail" class="flex flex-col gap-1 text-[length:var(--cd-text-sm)]">
            <p class="font-semibold" data-testid="lk-detail-naam">{{ detailNode.naam }}</p>
            <p><span class="text-[var(--cd-color-text-muted)]">Domein:</span> {{ detailNode.domein || '—' }}</p>
            <p><span class="text-[var(--cd-color-text-muted)]">Leverancier:</span> {{ detailNode.leverancier_naam || '—' }}</p>
            <p><span class="text-[var(--cd-color-text-muted)]">Hosting:</span> {{ detailNode.hosting_model ? typeLabel(detailNode.hosting_model) : '—' }}</p>
            <p><span class="text-[var(--cd-color-text-muted)]">Lifecycle:</span> <span class="inline-block rounded px-1" :style="{ background: lcStyle(detailNode.lifecycle_status).bg }">{{ detailNode.lifecycle_status ? typeLabel(detailNode.lifecycle_status) : '—' }}</span></p>
            <p><span class="text-[var(--cd-color-text-muted)]">Blokkades:</span> {{ detailNode.blokkades_open }}</p>
            <p><span class="text-[var(--cd-color-text-muted)]">Koppelingen:</span> {{ detailKoppelingen }}</p>
            <button v-if="isApplicatie(detailNode)" type="button" data-testid="lk-detail-open" class="mt-1 rounded-[var(--cd-radius-btn)] bg-[var(--cd-color-primary)] px-[var(--cd-space-sm)] py-1 text-white" @click="openApplicatie">Open applicatie →</button>
            <button type="button" :data-testid="`lk-detail-set`" class="rounded-[var(--cd-radius-btn)] border border-[var(--cd-color-border)] px-[var(--cd-space-sm)] py-1" @click="toggleSet(detailNode.id)">{{ inSet(detailNode.id) ? '× Verwijder uit set' : '+ Voeg toe aan set' }}</button>
          </div>
          <p v-else class="text-[length:var(--cd-text-xs)] text-[var(--cd-color-text-muted)]" data-testid="lk-detail-leeg">Klik een node voor detail.</p>
        </div>

        <div class="border-t border-[var(--cd-color-border)] pt-[var(--cd-space-sm)]" data-testid="lk-legenda">
          <p class="mb-1 font-semibold text-[length:var(--cd-text-sm)]">Legenda</p>
          <div class="flex flex-col gap-1 text-[length:var(--cd-text-sm)]">
            <span v-for="lc in LIFECYCLE_OPTIES.concat(['null'])" :key="lc" class="flex items-center gap-2">
              <span class="inline-block h-3 w-3 rounded-full" :style="{ background: lcStyle(lc).bg, border: `1px solid ${lcStyle(lc).border}` }"></span>{{ lc === 'null' ? 'geen profiel' : typeLabel(lc) }}
            </span>
            <span class="flex items-center gap-2">⚠ Open blokkade(s)</span>
            <span class="text-[length:var(--cd-text-xs)] text-[var(--cd-color-text-muted)]">Klik een node = detail</span>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>
