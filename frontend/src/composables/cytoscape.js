// Cytoscape via een frontend-wrapper (ADR-025). Module-views leven buiten `frontend/`, dus een
// bare `cytoscape`-import resolveert daar niet; door hier (binnen frontend/src) te re-exporteren
// loopt de package-resolutie via frontend/node_modules. Spiegelt `@/composables/router`.
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'

// Dagre-extensie eenmalig registreren (hiërarchische layout voor de Landschapskaart, ADR-025).
cytoscape.use(dagre)

export default cytoscape
