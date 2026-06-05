/**
 * PrimeVue PassThrough preset — DataTable (ADR-047 B6)
 */
export default {
  root: {
    class: 'font-[var(--cd-font-family)] text-[length:var(--cd-text-sm)]',
  },
  tableContainer: {
    class: 'overflow-x-auto',
  },
  table: {
    class: 'w-full border-collapse',
  },
  thead: {
    style: { background: 'var(--cd-color-primary)' },
  },
  headerRow: {},
  headerCell: {
    style: {
      background: 'var(--cd-color-primary)',
      color: 'white',
      fontWeight: '600',
      padding: '0.75rem 1rem',
      textAlign: 'left',
    },
  },
  bodyRow: ({ context }) => ({
    style: {
      background: context?.index % 2 === 0 ? 'white' : 'var(--cd-color-surface, #f9fafb)',
    },
    class: 'border-b border-[var(--cd-color-border,#e5e7eb)] hover:bg-[var(--cd-color-bg-hover,#f3f4f6)] transition-colors',
  }),
  bodyCell: {
    class: 'px-4 py-3 text-[var(--cd-color-text)]',
  },
  emptyMessage: {
    class: 'px-4 py-8 text-center text-gray-400',
  },
  sortIcon: {
    class: 'ml-1 text-[var(--cd-color-primary)]',
  },
  paginator: {
    root: {
      class: 'flex items-center justify-between px-4 py-3 border-t border-gray-200',
    },
    pages: {
      class: 'flex items-center gap-1',
    },
    pageButton: {
      class: [
        'min-w-[2rem] h-8 flex items-center justify-center',
        'rounded-[var(--cd-border-radius)]',
        'text-[length:var(--cd-text-sm)] text-[var(--cd-color-text)]',
        'hover:bg-[var(--cd-color-primary)] hover:text-white',
        'transition-colors cursor-pointer',
      ],
    },
  },
}
