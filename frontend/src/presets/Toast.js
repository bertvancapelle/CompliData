/**
 * PrimeVue PassThrough preset — Toast (ADR-047 B6)
 */
export default {
  root: {
    class: 'fixed top-4 right-4 z-60 flex flex-col gap-2',
  },
  message: ({ props }) => ({
    class: [
      'flex items-start gap-3 p-4 rounded-[var(--lk-border-radius)]',
      'shadow-[var(--lk-shadow-md)] min-w-[20rem] max-w-[25rem]',
      'font-[var(--lk-font-family)]',
      props.message?.severity === 'success' && 'bg-[var(--lk-color-success)] text-white',
      props.message?.severity === 'error' && 'bg-[var(--lk-color-danger)] text-white',
      props.message?.severity === 'warn' && 'bg-[var(--lk-color-warning)] text-white',
      (!props.message?.severity || props.message?.severity === 'info') && 'bg-[var(--lk-color-primary)] text-white',
    ],
  }),
  messageText: {
    class: 'flex flex-col gap-1',
  },
  summary: {
    class: 'font-semibold text-[length:var(--lk-text-sm)]',
  },
  detail: {
    class: 'text-[length:var(--lk-text-xs)] opacity-90',
  },
  closeButton: {
    class: 'ml-auto text-white/80 hover:text-white cursor-pointer',
  },
}
