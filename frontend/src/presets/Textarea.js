/**
 * PrimeVue PassThrough preset — Textarea (ADR-047 B6)
 */
export default {
  root: {
    class: [
      'w-full px-3 py-2',
      'rounded-[var(--lk-border-radius)]',
      'border border-gray-300',
      'font-[var(--lk-font-family)] text-[length:var(--lk-text-base)] text-[var(--lk-color-text)]',
      'bg-[var(--lk-color-surface)]',
      'placeholder:text-gray-400',
      'focus:outline-none focus:ring-2 focus:ring-[var(--lk-color-primary)] focus:border-[var(--lk-color-primary)]',
      'disabled:bg-gray-100 disabled:cursor-not-allowed',
      'transition-all duration-[var(--lk-transition-fast)]',
      'resize-y min-h-[5rem]',
    ],
  },
}
