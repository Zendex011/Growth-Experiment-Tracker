import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useExperiments } from '../hooks/useExperiment'
import ExperimentCard from '../components/ExperimentCard'
import StateBadge from '../components/StateBadge'

const FILTERS = [null, 'draft', 'running', 'paused', 'completed']
const FILTER_LABELS = { null: 'All', draft: 'Draft', running: 'Running', paused: 'Paused', completed: 'Completed' }

function SkeletonCard() {
  return (
    <div className="border border-subtle rounded-2xl p-5 space-y-3 animate-pulse">
      <div className="flex justify-between">
        <div className="shimmer-bg h-4 w-48 rounded" />
        <div className="shimmer-bg h-5 w-16 rounded-full" />
      </div>
      <div className="shimmer-bg h-3 w-full rounded" />
      <div className="shimmer-bg h-3 w-2/3 rounded" />
      <div className="flex justify-between mt-1">
        <div className="shimmer-bg h-3 w-24 rounded" />
        <div className="shimmer-bg h-3 w-20 rounded" />
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [activeFilter, setActiveFilter] = useState(null)
  const { data, loading, error, refetch } = useExperiments()

  const filtered = activeFilter
    ? data.filter((e) => e.state === activeFilter)
    : data

  const counts = data.reduce((acc, e) => {
    acc[e.state] = (acc[e.state] || 0) + 1
    return acc
  }, {})

  return (
    <div className="p-8 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8 animate-fade-up">
        <div>
          <h1 className="font-display font-800 text-2xl text-slate-white mb-1">
            Experiments
          </h1>
          <p className="text-sm text-slate-mid font-body">
            {data.length} total · {counts.running || 0} running
          </p>
        </div>
        <button
          onClick={() => navigate('/experiments/new')}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-signal-blue
            hover:bg-blue-500 text-white text-sm font-body font-medium
            transition-all active:scale-95"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Experiment
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1 animate-fade-up" style={{ animationDelay: '60ms' }}>
        {FILTERS.map((f) => (
          <button
            key={String(f)}
            onClick={() => setActiveFilter(f)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-body font-medium
              whitespace-nowrap transition-all shrink-0
              ${activeFilter === f
                ? 'bg-ink-muted border border-slate-edge text-slate-white'
                : 'text-slate-mid hover:text-slate-white'
              }`}
          >
            {FILTER_LABELS[f]}
            {f && counts[f] ? (
              <span className="font-mono text-slate-edge">{counts[f]}</span>
            ) : null}
          </button>
        ))}
      </div>

      {/* Content */}
      {error && (
        <div className="rounded-xl border border-signal-red border-opacity-40 bg-signal-red-dim p-4 mb-4">
          <p className="text-sm text-signal-red font-body">{error}</p>
          <button onClick={refetch} className="text-xs text-slate-soft mt-1 hover:text-slate-white">
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 animate-fade-in">
          <div className="w-12 h-12 rounded-2xl bg-ink-muted border border-subtle flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-slate-edge" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <p className="font-display font-600 text-slate-soft mb-1">
            {activeFilter ? `No ${activeFilter} experiments` : 'No experiments yet'}
          </p>
          <p className="text-sm text-slate-edge font-body mb-5">
            {activeFilter ? 'Try a different filter' : 'Create your first growth experiment'}
          </p>
          {!activeFilter && (
            <button
              onClick={() => navigate('/experiments/new')}
              className="px-5 py-2.5 rounded-xl bg-signal-blue hover:bg-blue-500 text-white
                text-sm font-body font-medium transition-all active:scale-95"
            >
              New Experiment
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((exp, i) => (
            <ExperimentCard key={exp.id} experiment={exp} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
