import { absoluteTime } from '../utils/format'

const EVENT_STYLES = {
  created:      { color: 'text-slate-soft',    dot: 'bg-slate-edge',    label: 'Created' },
  state_change: { color: 'text-signal-blue',   dot: 'bg-signal-blue',   label: 'State changed' },
  result_added: { color: 'text-signal-green',  dot: 'bg-signal-green',  label: 'Result logged' },
  verdict_set:  { color: 'text-signal-purple', dot: 'bg-signal-purple', label: 'Verdict set' },
}

function EventLabel({ log }) {
  if (log.event_type === 'state_change') {
    return (
      <span>
        <span className="text-slate-soft">{log.from_state}</span>
        <span className="text-slate-edge mx-1.5">→</span>
        <span className="text-slate-white">{log.to_state}</span>
      </span>
    )
  }
  if (log.event_type === 'verdict_set') {
    return (
      <span>
        Verdict set to <span className="text-signal-purple capitalize">{log.metadata?.verdict}</span>
      </span>
    )
  }
  if (log.event_type === 'result_added') {
    return (
      <span>
        Result logged
        {log.metadata?.control_value != null && (
          <span className="text-slate-mid ml-1">
            (control: {log.metadata.control_value}, variant: {log.metadata.variant_value})
          </span>
        )}
      </span>
    )
  }
  const style = EVENT_STYLES[log.event_type] ?? EVENT_STYLES.created
  return <span>{style.label}</span>
}

export default function AuditLog({ logs = [] }) {
  if (logs.length === 0) {
    return (
      <p className="text-sm text-slate-edge font-body py-4">No events yet.</p>
    )
  }

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-[7px] top-2 bottom-2 w-px bg-ink-muted" />

      <div className="space-y-4">
        {[...logs].reverse().map((log, i) => {
          const style = EVENT_STYLES[log.event_type] ?? EVENT_STYLES.created
          return (
            <div key={log.id} className="flex gap-4 items-start animate-fade-up"
              style={{ animationDelay: `${i * 40}ms`, animationFillMode: 'both', opacity: 0 }}>
              {/* Dot */}
              <div className={`w-3.5 h-3.5 rounded-full shrink-0 mt-0.5 border-2 border-ink ${style.dot}`} />

              <div className="flex-1 min-w-0 -mt-0.5">
                <p className={`text-sm font-body ${style.color}`}>
                  <EventLabel log={log} />
                </p>
                <p className="text-xs text-slate-edge font-mono mt-0.5">
                  {absoluteTime(log.created_at)}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
