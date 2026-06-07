// Nederlandse labels voor de Applicatie-enums — frontend-presentatiezaak.
// De backend levert alleen de waarden (codes); een waarde zonder expliciet label
// valt terug op een gehumaniseerde code, zodat een nieuwe backend-waarde nooit
// "leeg" in de UI verschijnt.

export function humaniseer(code) {
  if (code == null) return ''
  const tekst = String(code).replace(/_/g, ' ')
  return tekst.charAt(0).toUpperCase() + tekst.slice(1)
}

export function label(map, code) {
  return map[code] ?? humaniseer(code)
}

// `checklist_compleet` is transient (ADR-013 B4) en wordt nooit als ruststatus
// getoond; valt via de humanize-fallback op een generiek label terug.
export const LIFECYCLE = {
  concept: 'Concept',
  in_inventarisatie: 'In inventarisatie',
  geblokkeerd: 'Geblokkeerd',
  migratieklaar: 'Migratieklaar',
}

export const HOSTINGMODEL = {
  on_premise: 'On-premise',
  private_cloud: 'Private cloud',
  saas: 'SaaS',
  iaas: 'IaaS',
  paas: 'PaaS',
  hybride: 'Hybride',
  onbekend: 'Onbekend',
}

export const MIGRATIEPAD = {
  lift_and_shift: 'Lift-and-shift',
  herbouw: 'Herbouw',
  vervangen: 'Vervangen',
  uitfaseren: 'Uitfaseren',
  tijdelijk_gedeeld: 'Tijdelijk gedeeld',
  onbekend: 'Onbekend',
}

export const NIVEAU = {
  laag: 'Laag',
  midden: 'Midden',
  hoog: 'Hoog',
}

// Lifecycle-status → Tag-severity (Tag-preset kent info/success/warn/danger).
export const LIFECYCLE_SEVERITY = {
  concept: 'info',
  in_inventarisatie: 'warn',
  geblokkeerd: 'danger',
  migratieklaar: 'success',
}

// ── Child-entiteiten ─────────────────────────────────────────────────────────

export const DATATYPE_CATEGORIE = {
  gestructureerd_db: 'Gestructureerde database',
  documenten: 'Documenten',
  email: 'E-mail',
  spatial: 'Spatial / geo',
  binair: 'Binair',
  combinatie: 'Combinatie',
}

export const KOPPELRICHTING = {
  eenrichting: 'Eenrichting',
  tweerichting: 'Tweerichting',
}

export const KOPPELPROTOCOL = {
  api: 'API',
  bestandsuitwisseling: 'Bestandsuitwisseling',
  database_link: 'Database-link',
  middleware: 'Middleware',
  overig: 'Overig',
}

export const IMPACT_VERBREKING = {
  laag: 'Laag',
  midden: 'Midden',
  hoog: 'Hoog',
  kritiek: 'Kritiek',
}

export const IMPACT_SEVERITY = {
  laag: 'info',
  midden: 'warn',
  hoog: 'warn',
  kritiek: 'danger',
}

// ── Lifecycle (Checklistscore/Blokkade) ──────────────────────────────────────

export const SCORE = {
  ja: 'Ja',
  deels: 'Deels',
  nee: 'Nee',
  nvt: 'N.v.t.',
}

export const SCORE_SEVERITY = {
  ja: 'success',
  deels: 'warn',
  nee: 'danger',
  nvt: 'info',
}

export const BLOKKADE_STATUS = {
  open: 'Open',
  in_behandeling: 'In behandeling',
  opgelost: 'Opgelost',
}

export const BLOKKADE_STATUS_SEVERITY = {
  open: 'danger',
  in_behandeling: 'warn',
  opgelost: 'success',
}
