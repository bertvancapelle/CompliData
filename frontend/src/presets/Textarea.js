/**
 * PrimeVue PassThrough preset — Textarea (ADR-047 B6)
 */
export default {
  root: {
    class: [
      'w-full px-3 py-2',
      'rounded-[var(--cd-border-radius)]',
      'border border-gray-300',
      'font-[var(--cd-font-family)] text-[length:var(--cd-text-base)] text-[var(--cd-color-text)]',
      'bg-[var(--cd-color-surface)]',
      'placeholder:text-gray-400',
      'focus:outline-none focus:ring-2 focus:ring-[var(--cd-color-primary)] focus:border-[var(--cd-color-primary)]',
      'disabled:bg-gray-100 disabled:cursor-not-allowed',
      'transition-all duration-[var(--cd-transition-fast)]',
      'resize-y min-h-[5rem]',
    ],
  },
}
