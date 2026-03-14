import { STATE_META } from '../utils/states'

export default function StateBadge({ state, size = 'md' }) {
  const meta = STATE_META[state] ?? {
    label: state,
    color: 'text-slate-soft',
    bg: 'bg-ink-muted',
    border: 'border-slate-edge',
    dot: 'bg-slate-soft',
  }

  const sizes = {
    sm: 'text-xs px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-2',
    lg: 'text-sm px-3 py-1.5 gap-2',
  }

  const dotSizes = { sm: 'w-1.5 h-1.5', md: 'w-2 h-2', lg: 'w-2 h-2' }

  return (
    <span
      className={`inline-flex items-center rounded-full border font-mono font-medium tracking-wider uppercase
        ${meta.bg} ${meta.border} ${meta.color} ${sizes[size]}`}
    >
      <span
        className={`rounded-full shrink-0 ${meta.dot} ${dotSizes[size]} ${
          state === 'running' ? 'animate-pulse-soft' : ''
        }`}
      />
      {meta.label}
    </span>
  )
}
