import { useNavigate } from 'react-router-dom'
import StateBadge from './StateBadge'
import { VERDICT_META } from '../utils/states'
import { relativeTime, liftLabel } from '../utils/format'

export default function ExperimentCard({ experiment, index = 0 }) {
  const navigate = useNavigate()
  const result = experiment.results?.[0]
  const lift = result ? liftLabel(result.control_value, result.variant_value) : null
  const liftPositive = result ? result.variant_value >= result.control_value : null
  const verdict = experiment.verdict ? VERDICT_META[experiment.verdict] : null

  return (
    <div
      onClick={() => navigate(`/experiments/${experiment.id}`)}
      className="group relative border border-subtle rounded-2xl p-5 cursor-pointer
        hover:border-slate-edge hover:bg-ink-soft transition-all duration-200
        animate-fade-up"
      style={{ animationDelay: `${index * 60}ms`, animationFillMode: 'both', opacity: 0 }}
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="font-display font-600 text-sm text-slate-white leading-snug line-clamp-1 group-hover:text-white transition-colors">
          {experiment.title}
        </h3>
        <StateBadge state={experiment.state} size="sm" />
      </div>

      {/* Hypothesis */}
      <p className="text-xs text-slate-mid font-body leading-relaxed line-clamp-2 mb-4">
        {experiment.hypothesis}
      </p>

      {/* Metrics row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-slate-soft">
            {experiment.metric_name}
          </span>
          {lift && (
            <span className={`text-xs font-mono font-medium ${liftPositive ? 'text-signal-green' : 'text-signal-red'}`}>
              {lift}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {verdict && (
            <span className={`text-xs font-mono px-2 py-0.5 rounded-full border
              ${verdict.bg} ${verdict.border} ${verdict.color}`}>
              {verdict.icon} {verdict.label}
            </span>
          )}
          <span className="text-xs text-slate-edge font-body">
            {relativeTime(experiment.created_at)}
          </span>
        </div>
      </div>

      {/* Hover arrow */}
      <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        <svg className="w-4 h-4 text-slate-edge" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  )
}
