/**
 * PrimeVue PassThrough preset — Popover (ADR-047 B6).
 *
 * DOM-structuur PrimeVue 4.x:
 *   transition (p-anchored-overlay)
 *     └─ root      ← ptmi('root')      → bg + shadow + border + z-50
 *         └─ content ← ptm('content')   → padding + text-styling
 */
export default {
  root: {
    class: [
      'bg-[var(--cd-color-surface)]',
      'rounded-[var(--cd-radius-md,8px)]',
      'shadow-[var(--cd-shadow-lg)]',
      'border border-[var(--cd-color-border)]',
      'z-50',
    ],
  },
  content: {
    class: [
      'px-4 py-3',
      'text-[length:var(--cd-text-sm)]',
      'text-[var(--cd-color-text)]',
    ],
  },
}
