/**
 * PrimeVue PassThrough preset — Tag (ADR-047 B6)
 */
export default {
  root: ({ props }) => ({
    class: [
      'inline-flex items-center gap-1',
      'px-2 py-0.5 rounded-full',
      'font-[var(--cd-font-family)] text-[length:var(--cd-text-xs)] font-semibold',
      props.severity === 'success' && 'bg-[var(--cd-color-success)]/15 text-[var(--cd-color-success)]',
      props.severity === 'danger' && 'bg-[var(--cd-color-danger)]/15 text-[var(--cd-color-danger)]',
      props.severity === 'warn' && 'bg-[var(--cd-color-warning)]/15 text-[var(--cd-color-warning)]',
      (!props.severity || props.severity === 'info') && 'bg-[var(--cd-color-primary)]/15 text-[var(--cd-color-primary)]',
    ],
  }),
  label: {
    class: 'leading-normal',
  },
}
