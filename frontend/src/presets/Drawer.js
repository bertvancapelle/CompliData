/**
 * PrimeVue PassThrough preset — Drawer (ADR-047 B6).
 *
 * Minimale styling voor side-drawer met mask-overlay. Hergebruikt
 * canonieke Button-preset voor de sluit-knop via pcCloseButton.
 */
export default {
  mask: {
    class: 'fixed inset-0 z-40 bg-black/40 flex items-stretch justify-end',
  },
  root: {
    class: [
      'fixed top-0 right-0 h-screen z-50',
      'bg-white shadow-xl',
      'rounded-[var(--lk-radius-dialog)]',
      'flex flex-col',
      'transition-transform duration-300',
    ],
  },
  header: {
    class: 'flex items-center justify-between p-4 border-b border-gray-200',
  },
  title: {
    class: 'font-medium text-[length:var(--lk-text-base)] text-[var(--lk-color-text)]',
  },
  content: {
    class: 'flex-1 overflow-y-auto p-4',
  },
}
