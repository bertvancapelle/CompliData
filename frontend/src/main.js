import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import { router } from './router'
import App from './App.vue'
import presets from './presets'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
// PrimeVue Unstyled + centrale PassThrough presets (ADR-047)
app.use(PrimeVue, { unstyled: true, pt: presets })
app.use(ToastService)
app.mount('#app')
