<script setup>
/**
 * SignaleringBadge — kleine inline indicator van registratiegaten op een entiteit (ADR-035).
 * 🔴 N bij ≥1 kritiek; anders 🟡 N bij ≥1 aandacht; niets als beide 0.
 * Puur presentatie — laadt zelf niets; de ouder geeft de tellingen door.
 */
defineProps({
  kritiek: { type: Number, default: 0 },
  aandacht: { type: Number, default: 0 },
})
</script>

<template>
  <span
    v-if="kritiek > 0"
    data-testid="signalering-badge"
    :title="`${kritiek} kritiek(e) registratiegat(en)`"
    class="inline-flex items-center gap-0.5 rounded-[var(--cd-radius-badge)] bg-[var(--cd-color-danger)]/15 px-[var(--cd-space-xs)] py-0.5 text-[length:var(--cd-text-xs)] text-[var(--cd-color-danger)]"
  >🔴 {{ kritiek }}</span>
  <span
    v-else-if="aandacht > 0"
    data-testid="signalering-badge"
    :title="`${aandacht} aandachtspunt(en)`"
    class="inline-flex items-center gap-0.5 rounded-[var(--cd-radius-badge)] bg-[var(--cd-color-warning)]/15 px-[var(--cd-space-xs)] py-0.5 text-[length:var(--cd-text-xs)]"
  >🟡 {{ aandacht }}</span>
</template>
