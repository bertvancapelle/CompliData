/**
 * PrimeVue PassThrough preset — Button (ADR-047 B6)
 *
 * Function-based preset: leest `props.severity` en `props.size` zodat
 * views geen inline :pt= meer hoeven te geven. Ondersteunt:
 *   severity: undefined | 'secondary' | 'danger'
 *   size:     undefined | 'small'
 *
 * Canonieke Button-styling — views gebruiken
 * <Button severity="..." size="..." /> zonder :pt=. ACT-148 SC2.
 */
export default {
  root: ({ props }) => ({
    class: [
      'inline-flex items-center justify-center gap-2',
      'rounded-[var(--cd-radius-btn)]',
      'font-[var(--cd-font-family)]',
      'cursor-pointer transition-all duration-[var(--cd-transition-fast)]',
      'disabled:opacity-50 disabled:cursor-not-allowed',

      // Size-variant
      props.size === 'small'
        ? 'px-3 py-1 text-[length:var(--cd-text-xs)]'
        : 'px-4 py-2 text-[length:var(--cd-text-sm)]',

      // Severity-variant
      props.severity === 'danger'
        ? 'bg-[var(--cd-color-danger)] text-white hover:opacity-90'
        : props.severity === 'secondary'
          ? 'bg-transparent text-[var(--cd-color-text)] border border-gray-300 hover:bg-gray-50'
          : [
              'bg-[var(--cd-color-primary)] text-white',
              'hover:bg-[#2D6DB5]',
              'focus:outline-2 focus:outline-offset-2 focus:outline-[var(--cd-color-primary)]',
            ],
    ],
  }),
  label: {
    class: 'font-semibold',
  },
  icon: {
    class: 'text-[length:var(--cd-text-base)]',
  },
}
