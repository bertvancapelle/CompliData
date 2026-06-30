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
      'bg-[var(--lk-color-surface)]',
      'rounded-[var(--lk-radius-md,8px)]',
      'shadow-[var(--lk-shadow-lg)]',
      'border border-[var(--lk-color-border)]',
      'z-50',
    ],
  },
  content: {
    class: [
      'px-4 py-3',
      'text-[length:var(--lk-text-sm)]',
      'text-[var(--lk-color-text)]',
    ],
  },
}
