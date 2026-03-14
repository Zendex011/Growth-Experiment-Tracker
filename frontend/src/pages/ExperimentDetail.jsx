import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useExperiment } from '../hooks/useExperiment'
import { useAISuggestion } from '../hooks/useAISuggestion'
import { experiments as api } from '../api/experiments'
import StateBadge from '../components/StateBadge'
import StateTransition from '../components/StateTransition'
import ResultForm from '../components/ResultForm'
import VerdictForm from '../components/VerdictForm'
import AuditLog from '../components/AuditLog'
import AISuggestion from '../components/AISuggestion'
import { VERDICT_META } from '../utils/states'
import { absoluteTime, relativeTime, pct, liftLabel } from '../utils/format'

function Section({ title, children }) {
  return (
    <div className="border border-subtle rounded-2xl p-5">
      <h2 className="font-display font-600 text-xs uppercase tracking-widest text-slate-mid mb-4">
        {title}
      </h2>
      {children}
    </div>
  )
}

function MetricRow({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-subtle last:border-0">
      <span className="text-xs text-slate-mid font-body">{label}</span>
      <span className={`text-sm font-mono ${highlight ? 'text-slate-white' : 'text-slate-soft'}`}>
        {value}
      </span>
    </div>
  )
}

export default function ExperimentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { data: exp, loading, error, refetch, transition, setVerdict, addResult } = useExperiment(id)
  const { suggestion: summary, loading: summaryLoading, summarize } = useAISuggestion()
  const [deleting, setDeleting] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  if (loading) return (
    <div className="p-8 max-w-3xl mx-auto space-y-4">
      {[1, 2, 3].map(i => (
        <div key={i} className="border border-subtle rounded-2xl p-5 space-y-3 animate-pulse">
          <div className="shimmer-bg h-4 w-40 rounded" />
          <div className="shimmer-bg h-3 w-full rounded" />
          <div className="shimmer-bg h-3 w-3/4 rounded" />
        </div>
      ))}
    </div>
  )

  if (error) return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="rounded-2xl border border-signal-red border-opacity-40 bg-signal-red-dim p-6">
        <p className="text-signal-red font-body mb-3">{error}</p>
        <button onClick={() => navigate('/')} className="text-sm text-slate-soft hover:text-slate-white">
          ← Back to dashboard
        </button>
      </div>
    </div>
  )

  if (!exp) return null

  const result = exp.results?.[0]
  const verdict = exp.verdict ? VERDICT_META[exp.verdict] : null
  const hasResults = (exp.results?.length ?? 0) > 0

  const handleDelete = async () => {
    if (!window.confirm('Delete this experiment? This cannot be undone.')) return
    setDeleting(true)
    try {
      await api.delete(exp.id)
      navigate('/')
    } catch (err) {
      alert(err.message)
      setDeleting(false)
    }
  }

  const TABS = ['overview', 'results', 'audit']

  return (
    <div className="p-8 max-w-3xl mx-auto">

      {/* Back */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1.5 text-xs text-slate-mid hover:text-slate-white font-body mb-6 transition-colors"
      >
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Dashboard
      </button>

      {/* Header */}
      <div className="mb-6 animate-fade-up">
        <div className="flex items-start gap-3 mb-3">
          <h1 className="font-display font-800 text-2xl text-slate-white flex-1 leading-snug">
            {exp.title}
          </h1>
          <StateBadge state={exp.state} size="lg" />
        </div>

        {/* Verdict badge */}
        {verdict && (
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-sm font-body
            ${verdict.bg} ${verdict.border} ${verdict.color} mb-3`}>
            <span>{verdict.icon}</span>
            <span className="font-medium">{verdict.label}</span>
            {exp.verdict_reason && (
              <span className="text-xs opacity-70 ml-1">— {exp.verdict_reason}</span>
            )}
          </div>
        )}

        {/* Timestamps */}
        <div className="flex flex-wrap gap-4 text-xs font-mono text-slate-edge">
          <span>Created {relativeTime(exp.created_at)}</span>
          {exp.started_at && <span>Started {relativeTime(exp.started_at)}</span>}
          {exp.completed_at && <span>Completed {relativeTime(exp.completed_at)}</span>}
        </div>
      </div>

      {/* State transition controls */}
      {exp.state !== 'completed' && (
        <div className="mb-6 animate-fade-up" style={{ animationDelay: '60ms' }}>
          <StateTransition
            state={exp.state}
            hasResults={hasResults}
            onTransition={transition}
          />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-5 border-b border-subtle animate-fade-up" style={{ animationDelay: '80ms' }}>
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-xs font-body font-medium capitalize transition-all
              ${activeTab === tab
                ? 'text-slate-white border-b-2 border-signal-blue -mb-px'
                : 'text-slate-mid hover:text-slate-soft'
              }`}
          >
            {tab}
            {tab === 'results' && exp.results?.length > 0 && (
              <span className="ml-1.5 font-mono text-slate-edge">{exp.results.length}</span>
            )}
            {tab === 'audit' && exp.audit_logs?.length > 0 && (
              <span className="ml-1.5 font-mono text-slate-edge">{exp.audit_logs.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-4 animate-fade-up">

          <Section title="Hypothesis">
            <p className="text-sm text-slate-white font-body leading-relaxed">{exp.hypothesis}</p>
          </Section>

          <Section title="Metric">
            <MetricRow label="Metric name" value={exp.metric_name} highlight />
            <MetricRow label="Baseline" value={String(exp.metric_baseline)} />
            {result && (
              <>
                <MetricRow label="Control result" value={String(result.control_value)} />
                <MetricRow label="Variant result" value={String(result.variant_value)} />
                <MetricRow
                  label="Relative lift"
                  value={liftLabel(result.control_value, result.variant_value)}
                  highlight
                />
                <MetricRow label="Duration" value={`${result.duration_days} days`} />
                <MetricRow label="Sample (control)" value={result.sample_size_control.toLocaleString()} />
                <MetricRow label="Sample (variant)" value={result.sample_size_variant.toLocaleString()} />
              </>
            )}
          </Section>

          {/* Set verdict (completed, no verdict yet) */}
          {exp.state === 'completed' && !exp.verdict && (
            <Section title="Verdict">
              <VerdictForm onSubmit={(v, r) => setVerdict(v, r)} />
            </Section>
          )}

          {/* AI Summary (completed with verdict) */}
          {exp.state === 'completed' && exp.verdict && (
            <Section title="AI Summary">
              <div className="space-y-3">
                <button
                  onClick={() => summarize(exp.id)}
                  disabled={summaryLoading}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl border border-signal-blue
                    text-signal-blue bg-signal-blue-dim hover:bg-signal-blue hover:text-white
                    text-sm font-body transition-all active:scale-95 disabled:opacity-50"
                >
                  {summaryLoading
                    ? <span className="w-3.5 h-3.5 border border-current border-t-transparent rounded-full animate-spin" />
                    : <span>✦</span>}
                  Generate Summary
                </button>
                <AISuggestion
                  suggestion={summary}
                  loading={summaryLoading}
                  label="Experiment Summary"
                />
              </div>
            </Section>
          )}

          {/* Delete (draft only) */}
          {exp.state === 'draft' && (
            <div className="pt-2">
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="text-xs text-slate-edge hover:text-signal-red font-body transition-colors"
              >
                {deleting ? 'Deleting…' : 'Delete experiment'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab: Results */}
      {activeTab === 'results' && (
        <div className="space-y-4 animate-fade-up">
          {exp.state === 'running' && (
            <Section title="Log Result">
              <ResultForm
                experiment={exp}
                onSubmit={async (payload) => {
                  await addResult(payload)
                }}
              />
            </Section>
          )}

          {exp.results?.length > 0 ? (
            <Section title={`Results (${exp.results.length})`}>
              <div className="space-y-3">
                {exp.results.map((r, i) => (
                  <div key={r.id} className="rounded-xl bg-ink-muted border border-subtle p-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono text-slate-mid">Result #{i + 1}</span>
                      <span className="text-xs font-mono text-slate-edge">{absoluteTime(r.recorded_at)}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        ['Control', r.control_value],
                        ['Variant', r.variant_value],
                        ['Sample (ctrl)', r.sample_size_control.toLocaleString()],
                        ['Sample (var)', r.sample_size_variant.toLocaleString()],
                        ['Duration', `${r.duration_days}d`],
                        ['Lift', liftLabel(r.control_value, r.variant_value)],
                      ].map(([label, val]) => (
                        <div key={label}>
                          <p className="text-xs text-slate-edge font-body mb-0.5">{label}</p>
                          <p className="text-sm font-mono text-slate-white">{val}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Section>
          ) : (
            <div className="text-center py-12">
              <p className="text-sm text-slate-edge font-body">
                {exp.state === 'running'
                  ? 'No results logged yet. Use the form above.'
                  : 'No results were logged for this experiment.'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab: Audit */}
      {activeTab === 'audit' && (
        <div className="animate-fade-up">
          <Section title="Audit Trail">
            <AuditLog logs={exp.audit_logs ?? []} />
          </Section>
        </div>
      )}
    </div>
  )
}
