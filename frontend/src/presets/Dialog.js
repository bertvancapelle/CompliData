export default {
  root: {
    class: [
      'font-[var(--cd-font-family)]',
      'bg-[var(--cd-color-surface)]',
      'rounded-[var(--cd-radius-dialog)]',
      'shadow-[var(--cd-shadow-lg)]',
      'w-full max-w-lg mx-auto mt-[10vh]',
      'flex flex-col max-h-[80vh]',
    ],
  },
  mask: { class: 'fixed inset-0 bg-black/50 z-50' },
  header: {
    class: [
      'flex items-center justify-between',
      'px-6 pt-6 pb-2',
      'border-b border-[var(--cd-border)]',
    ],
  },
  title: {
    class: 'font-medium text-[length:var(--cd-text-base)] text-[var(--cd-text-primary)]',
  },
  headerActions: { class: 'flex items-center' },
  pcCloseButton: {
    root: { class: 'p-1 rounded hover:bg-[var(--cd-surface-alt)] text-[var(--cd-text-secondary)]' },
  },
  content: { class: ['px-6 py-4 overflow-y-auto', 'text-[var(--cd-text-primary)]'] },
  footer: { class: 'flex items-center justify-end gap-2 px-6 pb-6 pt-2' },
}
