/**
 * PrimeVue PassThrough preset — Tag (ADR-047 B6)
 */
export default {
  root: ({ props }) => ({
    class: [
      'inline-flex items-center gap-1',
      'px-2 py-0.5 rounded-full',
      'font-[var(--lk-font-family)] text-[length:var(--lk-text-xs)] font-semibold',
      props.severity === 'success' && 'bg-[var(--lk-color-success)]/15 text-[var(--lk-color-success)]',
      props.severity === 'danger' && 'bg-[var(--lk-color-danger)]/15 text-[var(--lk-color-danger)]',
      props.severity === 'warn' && 'bg-[var(--lk-color-warning)]/15 text-[var(--lk-color-warning)]',
      (!props.severity || props.severity === 'info') && 'bg-[var(--lk-color-primary)]/15 text-[var(--lk-color-primary)]',
    ],
  }),
  label: {
    class: 'leading-normal',
  },
}
